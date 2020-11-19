from odoo.tests import Form, TransactionCase


class TestInternalTransferWithAgreedAmount(TransactionCase):
    def setUp(self):
        super(TestInternalTransferWithAgreedAmount, self).setUp()
        self.currency_usd = self.env.ref("base.USD")
        self.currency_eur = self.env.ref("base.EUR")
        self.bank_journal_usd = self.env['account.journal'].create({
            'name': 'Bank US', 'type': 'bank', 'code': 'BNK68'})
        self.bank_journal_eur = self.env['account.journal'].create({
            'name': 'Bank EUR', 'type': 'bank', 'code': 'BNK67',
            'currency_id': self.currency_eur.id})
        self.payment_method_manual = self.env.ref(
            "account.account_payment_method_manual_in")

    def create_internal_transfer(self, currency, journal, destination_journal, amount):
        transfer = Form(self.env['account.payment'])
        transfer.payment_type = 'transfer'
        transfer.journal_id = journal
        transfer.currency_id = currency
        transfer.destination_journal_id = destination_journal
        transfer.amount = amount
        return transfer.save()

    def create_multicurrency_transfer(self, payment, agreed_amount, currency):
        ctx = {'active_model': payment._name, 'active_ids': payment.ids}
        wizard = Form(self.env['internal.transfer.multicurrency'].with_context(**ctx))
        wizard.agreed_amount = agreed_amount
        wizard.currency_id = currency
        wizard = wizard.save()
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
        self.assertRecordValues(usd_aml, [{
            'balance': -100.0,  # payment amount
            'amount_currency': 0.0,
            'currency_id': False,
        }])

        # Check journal item in EUR
        eur_aml = transfer.move_line_ids.filtered(
            lambda m: m.account_id == transfer.destination_journal_id.default_credit_account_id)
        self.assertRecordValues(eur_aml, [{
            'balance': 100.0,  # payment amount
            'amount_currency': 120.0,  # Agreed amount
            'currency_id': self.currency_eur.id,
        }])

    def test_02_transfer_eur_usd(self):
        transfer = self.create_internal_transfer(
            self.currency_eur, self.bank_journal_eur,
            self.bank_journal_usd, 100)
        self.create_multicurrency_transfer(transfer, 80, self.currency_usd)

        # Check journal item in USD
        usd_aml = transfer.move_line_ids.filtered(
            lambda m: m.account_id == transfer.destination_journal_id.default_credit_account_id)
        self.assertRecordValues(usd_aml, [{
            'balance': 80.0,  # Agreed amount
            'amount_currency': 0.0,
            'currency_id': False,
        }])

        # Check journal item in EUR
        eur_aml = transfer.move_line_ids.filtered(
            lambda m: m.account_id == transfer.journal_id.default_credit_account_id)
        self.assertRecordValues(eur_aml, [{
            'balance': -80.0,  # Agreed amount
            'amount_currency': -100.0,  # Payment amount
            'currency_id': self.currency_eur.id,
        }])
