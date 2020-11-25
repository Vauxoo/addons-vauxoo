from odoo.tests import TransactionCase


class TestInternalTransferWithAgreedAmount(TransactionCase):
    def setUp(self):
        super(TestInternalTransferWithAgreedAmount, self).setUp()
        self.currency_usd = self.env.ref("base.USD")
        self.currency_eur = self.env.ref("base.EUR")
        self.bank_journal_usd = self.env['account.journal'].create({
            'name': 'Bank US', 'type': 'bank', 'code': 'BNK68',
            'update_posted': True})
        self.bank_journal_eur = self.env['account.journal'].create({
            'name': 'Bank EUR', 'type': 'bank', 'code': 'BNK67',
            'currency_id': self.currency_eur.id, 'update_posted': True})
        self.payment_method_manual = self.env.ref(
            "account.account_payment_method_manual_in")

    def create_internal_transfer(self, currency, journal, destination_journal, amount):
        transfer = self.env['account.payment'].create({
            'payment_type': 'transfer',
            'journal_id': journal.id,
            'currency_id': currency.id,
            'destination_journal_id': destination_journal.id,
            'payment_method_id': self.payment_method_manual.id,
            'amount': amount})
        return transfer

    def create_multicurrency_transfer(self, payment, agreed_amount, currency):
        ctx = {'active_model': payment._name, 'active_ids': payment.ids}
        wizard = self.env['internal.transfer.multicurrency'].with_context(**ctx).create({
            'agreed_amount': agreed_amount,
            'currency_id': currency.id,
        })
        wizard.apply()
        return wizard

    def test_01_transfer_usd_eur(self):
        transfer = self.create_internal_transfer(
            self.currency_usd, self.bank_journal_usd,
            self.bank_journal_eur, 100)
        self.create_multicurrency_transfer(transfer, 120, self.currency_eur)

        # Check journal item in USD
        usd_aml = transfer.move_line_ids.filtered(
            lambda m: m.account_id == transfer.journal_id.default_debit_account_id)
        self.assertEquals(usd_aml.balance, -100.0)  # payment amount
        self.assertEquals(usd_aml.amount_currency, 0.0)
        self.assertFalse(usd_aml.currency_id)

        # Check journal item in EUR
        eur_aml = transfer.move_line_ids.filtered(
            lambda m: m.account_id == transfer.destination_journal_id.default_credit_account_id)
        self.assertEquals(eur_aml.balance, 100.0)  # payment amount
        self.assertEquals(eur_aml.amount_currency, 120.0)  # agreed amount
        self.assertEquals(eur_aml.currency_id, self.currency_eur)

    def test_02_transfer_eur_usd(self):
        transfer = self.create_internal_transfer(
            self.currency_eur, self.bank_journal_eur,
            self.bank_journal_usd, 100)
        self.create_multicurrency_transfer(transfer, 80, self.currency_usd)

        # Check journal item in USD
        usd_aml = transfer.move_line_ids.filtered(
            lambda m: m.account_id == transfer.destination_journal_id.default_credit_account_id)
        self.assertEquals(usd_aml.balance, 80.0)  # agreed amount
        self.assertEquals(usd_aml.amount_currency, 0.0)
        self.assertFalse(usd_aml.currency_id)

        # Check journal item in EUR
        eur_aml = transfer.move_line_ids.filtered(
            lambda m: m.account_id == transfer.journal_id.default_credit_account_id)
        self.assertEquals(eur_aml.balance, -80.0)  # agreed amount
        self.assertEquals(eur_aml.amount_currency, -100.0)
        self.assertEquals(eur_aml.currency_id, self.currency_eur)
