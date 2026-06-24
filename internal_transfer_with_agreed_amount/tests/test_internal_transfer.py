from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestInternalTransferMulticurrency(TransactionCase):
    """Unit tests for the Internal Transfer with Agreed Amount wizard.

    Company currency: MXN (Mexican Peso) — represents a typical Mexican company
    with operations in USD and EUR.

    Journals:
        BBVA 3889      — fixed USD currency (out for Cases 1, 2, 3b)
        HSBC 8792      — no fixed currency, editable (in for Cases 1, 2, 3a)
        CITYBANAMEX 5623 — no fixed currency, editable (out for Cases 3a, 4)
        MONEX 2309     — no fixed currency, editable (in for Cases 3b, 4)
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.mxn = cls.env.ref("base.MXN")
        cls.usd = cls.env.ref("base.USD")
        cls.eur = cls.env.ref("base.EUR")

        # Activate all currencies used in tests (may be inactive in a fresh test DB)
        (cls.mxn | cls.usd | cls.eur).write({"active": True})

        # Mexican company: company_currency_id = MXN
        cls.company = cls.env["res.company"].create(
            {
                "name": "Test MXN Company",
                "currency_id": cls.mxn.id,
            }
        )
        # Grant the test user access to cls.company so that allowed_company_ids
        # context switches are respected by ir.rules multi-company filters.
        cls.env.user.write({"company_ids": [(4, cls.company.id)]})
        env = cls.env(context=dict(cls.env.context, allowed_company_ids=[cls.company.id]))

        # Minimal chart of accounts for the test company.
        # Odoo 19: account.account uses company_ids (many2many) instead of company_id.
        def make_account(code, name, reconcile=False):
            return env["account.account"].create(
                {
                    "code": code,
                    "name": name,
                    "account_type": "asset_current",
                    "reconcile": reconcile,
                    "company_ids": [Command.set([cls.company.id])],
                }
            )

        cls.account_transfer = make_account("1010", "Internal Transfer Account", reconcile=True)
        # Outstanding accounts must be reconcilable so _compute_state stays 'in_process'
        # until matched with a bank statement (same as real Odoo setup).
        cls.account_out_payments = make_account("1020", "Outstanding Payments", reconcile=True)
        cls.account_in_receipts = make_account("1030", "Outstanding Receipts", reconcile=True)

        cls.company.transfer_account_id = cls.account_transfer

        # Journals
        def make_journal(name, code, currency=None):
            vals = {
                "name": name,
                "code": code,
                "type": "bank",
                "company_id": cls.company.id,
            }
            if currency:
                vals["currency_id"] = currency.id
            return env["account.journal"].create(vals)

        cls.j_bbva = make_journal("BBVA 3889", "BBVA", cls.usd)  # Fixed USD
        cls.j_hsbc = make_journal("HSBC 8792", "HSBC")  # No fixed currency
        cls.j_citybanamex = make_journal("CITYBANAMEX 5623", "CITY")  # No fixed currency
        cls.j_monex = make_journal("MONEX 2309", "MNEX")  # No fixed currency

        # Configure payment accounts on method lines.
        # Out journals get cls.account_out_payments on their outbound line,
        # in journals get cls.account_in_receipts on their inbound line.
        # Using different accounts ensures ADR6 (different payment accounts) is satisfied.
        for journal in (cls.j_bbva, cls.j_citybanamex):
            outbound = journal.outbound_payment_method_line_ids[:1]
            if outbound:
                outbound.payment_account_id = cls.account_out_payments

        for journal in (cls.j_hsbc, cls.j_monex):
            inbound = journal.inbound_payment_method_line_ids[:1]
            if inbound:
                inbound.payment_account_id = cls.account_in_receipts

        # Second company — used only in ADR4 cross-company negative tests.
        cls.company2 = cls.env["res.company"].create({"name": "Test Company 2", "currency_id": cls.mxn.id})
        cls.env.user.write({"company_ids": [(4, cls.company2.id)]})
        env2 = cls.env(context=dict(cls.env.context, allowed_company_ids=[cls.company2.id]))
        cls.j_company2 = env2["account.journal"].create(
            {
                "name": "Company 2 Journal",
                "code": "CO2J",
                "type": "bank",
                "company_id": cls.company2.id,
            }
        )

    # ── helpers ──────────────────────────────────────────────────────────────

    def _wizard(
        self,
        out_journal,
        out_currency,
        out_amount_currency,
        out_amount,
        in_journal,
        in_currency,
        in_amount_currency,
        memo="",
    ):
        """Create the wizard with all required fields.

        out_payment_method_line_id and in_payment_method_line_id are set
        automatically by their compute methods (_compute_*_payment_method_line_id)
        which pick the first method line that has payment_account_id configured.
        """
        env = self.env(context=dict(self.env.context, allowed_company_ids=[self.company.id]))
        return (
            env["internal.transfer.multicurrency"]
            .with_context(
                default_journal_id=out_journal.id,
            )
            .create(
                {
                    "company_id": self.company.id,
                    "out_journal_id": out_journal.id,
                    "out_currency_id": out_currency.id,
                    "out_amount_currency": out_amount_currency,
                    "out_amount": out_amount,
                    "in_journal_id": in_journal.id,
                    "in_currency_id": in_currency.id,
                    "in_amount_currency": in_amount_currency,
                    "memo": memo,
                }
            )
        )

    def _assert_payments(
        self,
        out_journal,
        out_currency,
        out_amount,
        in_journal,
        in_currency,
        in_amount,
    ):
        """Assert that two posted, linked payments were created with the expected values.

        Uses order='id desc' so within a rolled-back test the most recent record
        is picked unambiguously.

        Uses sudo() + explicit company_id filter to bypass company access rules:
        the test user is not a member of cls.company, so standard env would
        not return payments belonging to it.
        """
        payment_model = self.env["account.payment"].sudo()
        # In Odoo 19, payment state after action_post() is 'in_process' (not 'posted').
        # 'posted' does not exist; the three states are: draft, in_process, paid.
        domain_base = [
            ("is_internal_transfer", "=", True),
            ("state", "=", "in_process"),
            ("company_id", "=", self.company.id),
        ]
        out_pay = payment_model.search(
            domain_base + [("journal_id", "=", out_journal.id), ("payment_type", "=", "outbound")],
            order="id desc",
            limit=1,
        )
        in_pay = payment_model.search(
            domain_base + [("journal_id", "=", in_journal.id), ("payment_type", "=", "inbound")],
            order="id desc",
            limit=1,
        )

        self.assertTrue(out_pay, "Outbound payment was not created")
        self.assertTrue(in_pay, "Inbound payment was not created")

        self.assertEqual(out_pay.currency_id, out_currency)
        self.assertAlmostEqual(out_pay.amount, out_amount, places=2)

        self.assertEqual(in_pay.currency_id, in_currency)
        self.assertAlmostEqual(in_pay.amount, in_amount, places=2)

        # Both payments must reference each other (paired_internal_transfer_payment_id)
        self.assertEqual(out_pay.paired_internal_transfer_payment_id, in_pay)
        self.assertEqual(in_pay.paired_internal_transfer_payment_id, out_pay)

    # ── test cases ───────────────────────────────────────────────────────────

    def test_caso1_different_currencies_not_company_currency(self):
        """Case 1 — DIFFERENT CURRENCIES (both ≠ company currency MXN)

        out: BBVA 3889 (USD fixed)  →  1,000 USD  /  17,500 MXN local
        in:  HSBC 8792 (EUR manual) →    950 EUR

        ADR2 — BBVA ≠ HSBC → different journals ✓
        ADR3 — USD ≠ EUR → no equal-amount constraint; 1,000 USD ≠ 950 EUR accepted ✓
        ADR4 — same company ✓
        ADR5 — out_currency (USD) ≠ company_currency (MXN) → out_amount_currency and
               out_amount may differ; 1,000 USD / 17,500 MXN accepted ✓
        ADR6 — account_out_payments ≠ account_in_receipts ✓
        """
        wizard = self._wizard(
            self.j_bbva,
            self.usd,
            1_000.0,
            17_500.0,
            self.j_hsbc,
            self.eur,
            950.0,
        )
        wizard.action_create_internal_transfer()
        self._assert_payments(
            self.j_bbva,
            self.usd,
            1_000.0,
            self.j_hsbc,
            self.eur,
            950.0,
        )

    def test_caso2_same_currency_not_company_currency(self):
        """Case 2 — SAME CURRENCY (both USD, ≠ company currency MXN)

        out: BBVA 3889 (USD fixed)    → 1,000 USD / 17,500 MXN local
        in:  HSBC 8792 (USD editable) → 1,000 USD

        ADR3 — USD == USD → sent and received amounts must be equal;
               1,000 USD == 1,000 USD → valid ✓
        ADR5 — out_currency (USD) ≠ company_currency (MXN) → no out_amount constraint ✓
        """
        wizard = self._wizard(
            self.j_bbva,
            self.usd,
            1_000.0,
            17_500.0,
            self.j_hsbc,
            self.usd,
            1_000.0,
        )
        wizard.action_create_internal_transfer()
        self._assert_payments(
            self.j_bbva,
            self.usd,
            1_000.0,
            self.j_hsbc,
            self.usd,
            1_000.0,
        )

    def test_caso3a_company_currency_on_out_side(self):
        """Case 3a — DIFFERENT CURRENCIES (company_currency MXN is the OUT side)

        out: CITYBANAMEX 5623 (MXN editable) → 17,500 MXN / 17,500 MXN local
        in:  HSBC 8792 (EUR editable)         →    950 EUR

        ADR3 — MXN ≠ EUR → no equal-amount constraint ✓
        ADR5 (sending) — out_currency (MXN) == company_currency (MXN) →
               out_amount_currency must equal out_amount;
               17,500 MXN == 17,500 MXN → valid ✓
        """
        wizard = self._wizard(
            self.j_citybanamex,
            self.mxn,
            17_500.0,
            17_500.0,
            self.j_hsbc,
            self.eur,
            950.0,
        )
        wizard.action_create_internal_transfer()
        self._assert_payments(
            self.j_citybanamex,
            self.mxn,
            17_500.0,
            self.j_hsbc,
            self.eur,
            950.0,
        )

    def test_caso3b_company_currency_on_in_side(self):
        """Case 3b — DIFFERENT CURRENCIES (company_currency MXN is the IN side)
        Symmetric to 3a: company currency on the receiving side.

        out: BBVA 3889 (USD fixed)    →  1,000 USD / 17,500 MXN local
        in:  MONEX 2309 (MXN editable)→ 17,500 MXN

        ADR3 — USD ≠ MXN → no equal-amount constraint ✓
        ADR5 (sending) — out_currency (USD) ≠ company_currency (MXN) →
               no constraint between out_amount_currency and out_amount ✓
        ADR5 (receiving) — in_currency (MXN) == company_currency (MXN) →
               in_amount_currency must equal out_amount; 17,500 MXN == 17,500 MXN ✓
        """
        wizard = self._wizard(
            self.j_bbva,
            self.usd,
            1_000.0,
            17_500.0,
            self.j_monex,
            self.mxn,
            17_500.0,
        )
        wizard.action_create_internal_transfer()
        self._assert_payments(
            self.j_bbva,
            self.usd,
            1_000.0,
            self.j_monex,
            self.mxn,
            17_500.0,
        )

    def test_caso4_both_company_currency(self):
        """Case 4 — ALL IN COMPANY CURRENCY (both sides MXN)

        out: CITYBANAMEX 5623 (MXN editable) → 17,500 MXN / 17,500 MXN local
        in:  MONEX 2309 (MXN editable)        → 17,500 MXN

        ADR3 — MXN == MXN → amounts must be equal;
               17,500 MXN == 17,500 MXN → valid ✓
        ADR5 (sending) — out_currency (MXN) == company_currency (MXN) →
               out_amount_currency must equal out_amount;
               17,500 MXN == 17,500 MXN → valid ✓
        """
        wizard = self._wizard(
            self.j_citybanamex,
            self.mxn,
            17_500.0,
            17_500.0,
            self.j_monex,
            self.mxn,
            17_500.0,
        )
        wizard.action_create_internal_transfer()
        self._assert_payments(
            self.j_citybanamex,
            self.mxn,
            17_500.0,
            self.j_monex,
            self.mxn,
            17_500.0,
        )

    # ── negative test cases ──────────────────────────────────────────────────

    def test_adr2_n1_same_journal(self):
        """ADR2-N1 — same journal for out and in → UserError on create."""
        with self.assertRaises(UserError):
            self._wizard(
                self.j_bbva,
                self.usd,
                1_000.0,
                17_500.0,
                self.j_bbva,
                self.usd,
                1_000.0,
            )

    def test_adr3_n1_same_foreign_currency_different_amounts(self):
        """ADR3-N1 — both USD (foreign), amounts differ (1,000 ≠ 900) → UserError on create."""
        with self.assertRaises(UserError):
            self._wizard(
                self.j_bbva,
                self.usd,
                1_000.0,
                17_500.0,
                self.j_hsbc,
                self.usd,
                900.0,
            )

    def test_adr3_n2_same_company_currency_different_amounts(self):
        """ADR3-N2 — both MXN (company currency), amounts differ (17,500 ≠ 15,000) → UserError on create."""
        with self.assertRaises(UserError):
            self._wizard(
                self.j_citybanamex,
                self.mxn,
                17_500.0,
                17_500.0,
                self.j_monex,
                self.mxn,
                15_000.0,
            )

    def test_adr4_n1_out_journal_wrong_company(self):
        """ADR4-N1 — out_journal belongs to company2, wizard company_id is cls.company → UserError on create."""
        env = self.env(
            context=dict(
                self.env.context,
                allowed_company_ids=[self.company.id, self.company2.id],
            )
        )
        with self.assertRaises(UserError):
            env["internal.transfer.multicurrency"].with_context(
                default_journal_id=self.j_bbva.id,
            ).create(
                {
                    "company_id": self.company.id,
                    "out_journal_id": self.j_company2.id,
                    "out_currency_id": self.mxn.id,
                    "out_amount_currency": 1_000.0,
                    "out_amount": 1_000.0,
                    "in_journal_id": self.j_hsbc.id,
                    "in_currency_id": self.eur.id,
                    "in_amount_currency": 950.0,
                }
            )

    def test_adr4_n2_in_journal_wrong_company(self):
        """ADR4-N2 — in_journal belongs to company2, wizard company_id is cls.company → UserError on create."""
        env = self.env(
            context=dict(
                self.env.context,
                allowed_company_ids=[self.company.id, self.company2.id],
            )
        )
        with self.assertRaises(UserError):
            env["internal.transfer.multicurrency"].with_context(
                default_journal_id=self.j_bbva.id,
            ).create(
                {
                    "company_id": self.company.id,
                    "out_journal_id": self.j_bbva.id,
                    "out_currency_id": self.usd.id,
                    "out_amount_currency": 1_000.0,
                    "out_amount": 17_500.0,
                    "in_journal_id": self.j_company2.id,
                    "in_currency_id": self.mxn.id,
                    "in_amount_currency": 1_000.0,
                }
            )

    def test_adr5_n1_company_currency_out_mismatched_local_amount(self):
        """ADR5-N1 — out_currency MXN (company), out_amount_currency ≠ out_amount (17,500 ≠ 20,000) → UserError on create."""
        with self.assertRaises(UserError):
            self._wizard(
                self.j_citybanamex,
                self.mxn,
                17_500.0,
                20_000.0,
                self.j_hsbc,
                self.eur,
                950.0,
            )

    def test_adr5_n2_company_currency_in_mismatched_local_amount(self):
        """ADR5-N2 — in_currency MXN (company), in_amount_currency ≠ out_amount (16,500 ≠ 17,500) → UserError on create.

        Symmetric to ADR5-N1: the receiving journal uses company currency MXN but the
        amount received does not match the agreed local amount.
        """
        with self.assertRaises(UserError):
            self._wizard(
                self.j_bbva,
                self.usd,
                1_000.0,
                17_500.0,
                self.j_monex,
                self.mxn,
                16_500.0,
            )

    def test_adr6_n3_same_payment_accounts(self):
        """ADR6-N3 — out and in methods share the same payment_account_id → UserError on create."""
        env = self.env(context=dict(self.env.context, allowed_company_ids=[self.company.id]))
        j_shared = env["account.journal"].create(
            {
                "name": "Shared Account Journal",
                "code": "SHRD",
                "type": "bank",
                "company_id": self.company.id,
            }
        )
        inbound = j_shared.inbound_payment_method_line_ids[:1]
        if inbound:
            inbound.payment_account_id = self.account_out_payments
        with self.assertRaises(UserError):
            self._wizard(
                self.j_bbva,
                self.usd,
                1_000.0,
                17_500.0,
                j_shared,
                self.usd,
                1_000.0,
            )

    def test_adr6_n4_no_payment_method_configured(self):
        """ADR6-N4 — out journal has no payment method with account → UserError at action time."""
        env = self.env(context=dict(self.env.context, allowed_company_ids=[self.company.id]))
        j_unconfigured = env["account.journal"].create(
            {
                "name": "Unconfigured Journal",
                "code": "UCFG",
                "type": "bank",
                "company_id": self.company.id,
            }
        )
        # No payment_account_id on any method line → out_payment_method_line_id stays empty.
        # _validate_before_create catches this when action_create_internal_transfer() is called.
        wizard = (
            env["internal.transfer.multicurrency"]
            .with_context(
                default_journal_id=j_unconfigured.id,
            )
            .create(
                {
                    "company_id": self.company.id,
                    "out_journal_id": j_unconfigured.id,
                    "out_currency_id": self.mxn.id,
                    "out_amount_currency": 1_000.0,
                    "out_amount": 1_000.0,
                    "in_journal_id": self.j_hsbc.id,
                    "in_currency_id": self.eur.id,
                    "in_amount_currency": 950.0,
                }
            )
        )
        with self.assertRaises(UserError):
            wizard.action_create_internal_transfer()

    def test_prerequisite_n1_no_transfer_account(self):
        """P-N1 — company has no transfer_account_id → UserError at action time."""
        self.company.write({"transfer_account_id": False})
        wizard = self._wizard(
            self.j_bbva,
            self.usd,
            1_000.0,
            17_500.0,
            self.j_hsbc,
            self.eur,
            950.0,
        )
        with self.assertRaises(UserError):
            wizard.action_create_internal_transfer()
