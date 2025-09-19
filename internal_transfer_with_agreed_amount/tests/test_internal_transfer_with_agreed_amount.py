from odoo.tests import Form, TransactionCase, tagged


@tagged("internal_transfer_multicurrency", "post_install", "-at_install")
class TestInternalTransferWithAgreedAmount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.currency = cls.env.ref("base.USD")
        cls.currency_foreign = cls.env.ref("base.EUR")
        cls.currency.active = True
        cls.currency_foreign.active = True
        cls.main_company = cls.env["res.company"].create({"name": "USD Company", "currency_id": cls.currency.id})
        cls.env.user.company_ids |= cls.main_company
        cls.env.user.company_id = cls.main_company
        transfer_account = cls.env["account.account"].create(
            {
                "name": "Liquidity Transfer",
                "code": "123456",
                "reconcile": True,
                "company_id": cls.main_company.id,
            }
        )
        journal_payment_account = transfer_account.copy()
        cls.main_company.write(
            {
                "transfer_account_id": transfer_account.id,
                "account_journal_payment_credit_account_id": journal_payment_account.id,
                "account_journal_payment_debit_account_id": journal_payment_account.id,
            }
        )
        cls.bank_journal = cls.env["account.journal"].create(
            {
                "name": "Bank " + cls.currency.name,
                "type": "bank",
                "currency_id": cls.currency.id,
                "company_id": cls.main_company.id,
            }
        )
        cls.bank_journal_foreign = cls.env["account.journal"].create(
            {
                "name": "Bank " + cls.currency_foreign.name,
                "type": "bank",
                "currency_id": cls.currency_foreign.id,
                "company_id": cls.main_company.id,
            }
        )

    def create_internal_transfer(self, currency, journal, destination_journal, amount):
        transfer = Form(self.env["account.payment"])
        transfer.payment_type = "outbound"
        transfer.journal_id = journal
        transfer.currency_id = currency
        transfer.is_internal_transfer = True
        transfer.destination_journal_id = destination_journal
        transfer.amount = amount
        return transfer.save()

    def create_multicurrency_transfer(self, payment, agreed_amount):
        ctx = {"active_model": payment._name, "active_ids": payment.ids}
        wizard = Form(self.env["internal.transfer.multicurrency"].with_context(**ctx))
        wizard.agreed_amount = agreed_amount
        wizard = wizard.save()
        wizard.apply()
        return wizard

    def test_01_transfer_local_foreign(self):
        transfer = self.create_internal_transfer(self.currency, self.bank_journal, self.bank_journal_foreign, 100)
        self.create_multicurrency_transfer(transfer, 120)

        # Check journal item in local currency
        aml = transfer.line_ids.filtered("reconciled")
        self.assertRecordValues(
            aml,
            [
                {
                    "balance": 100.0,  # payment amount
                    "amount_currency": 120.0,
                    "currency_id": self.currency_foreign.id,
                }
            ],
        )

        # Check journal item in foreign currency
        eur_aml = aml.full_reconcile_id.reconciled_line_ids.filtered(lambda line: line != aml)
        self.assertRecordValues(
            eur_aml,
            [
                {
                    "balance": -100.0,  # payment amount
                    "amount_currency": -120.0,  # Agreed amount
                    "currency_id": self.currency_foreign.id,
                }
            ],
        )

    def test_02_transfer_foreign_local(self):
        transfer = self.create_internal_transfer(
            self.currency_foreign, self.bank_journal_foreign, self.bank_journal, 100
        )
        self.create_multicurrency_transfer(transfer, 80)

        # Check journal item in local currency
        aml = transfer.line_ids.filtered("reconciled")
        self.assertRecordValues(
            aml,
            [
                {
                    "balance": 80.0,  # Agreed amount
                    "amount_currency": 100.0,
                    "currency_id": self.currency_foreign.id,
                }
            ],
        )

        # Check journal item in foreign currency
        eur_aml = aml.full_reconcile_id.reconciled_line_ids.filtered(lambda line: line != aml)
        self.assertRecordValues(
            eur_aml,
            [
                {
                    "balance": -80.0,  # Agreed amount
                    "amount_currency": -100.0,  # Payment amount
                    "currency_id": self.currency_foreign.id,
                }
            ],
        )
