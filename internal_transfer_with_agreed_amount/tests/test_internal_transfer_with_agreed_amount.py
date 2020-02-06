# Copyright 2020 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase
from odoo import fields


class TestInternalTransferWithAgreedAmount(TransactionCase):
    def setUp(self):
        super(TestInternalTransferWithAgreedAmount, self).setUp()
        self.payment_model = self.env['account.payment']
        self.wizard_model = self.env['internal.transfer.multicurrency']
        self.currency_usd = self.env.ref("base.USD")
        self.currency_mxn = self.env.ref("base.MXN")
        self.bank_journal_usd = self.env['account.journal'].create({
            'name': 'Bank US', 'type': 'bank', 'code': 'BNK68',
            'currency_id': self.currency_usd.id, 'update_posted': True})
        self.bank_journal_mxn = self.env['account.journal'].create({
            'name': 'Bank MXN', 'type': 'bank', 'code': 'BNK67',
            'update_posted': True})
        self.payment_method_manual = self.env.ref(
            "account.account_payment_method_manual_in")

    def create_internal_transfer(self, currency_id, journal_id,
                                 destination_journal_id, amount):
        transfer = Form(self.payment_model,
                        view="account.view_account_payment_form")
        transfer.payment_date = fields.Date.from_string('2020-01-01')
        transfer.payment_type = 'transfer'
        transfer.journal_id = journal_id
        transfer.currency_id = currency_id
        transfer.destination_journal_id = destination_journal_id
        transfer.amount = amount
        return transfer.save()

    def test_01_transfer_usd_mxn(self):
        transfer = self.create_internal_transfer(
            self.currency_usd, self.bank_journal_usd,
            self.bank_journal_mxn, 100)
        ctx = {'active_model': self.payment_model._name,
               'active_ids': transfer.ids}
        wizard = self.wizard_model.with_context(ctx).create(
            {'agreed_amount': 2000, 'currency_id': self.currency_mxn.id})
        wizard.apply()
        usd_aml = transfer.move_line_ids.filtered(
            lambda m: m.account_id ==
            transfer.journal_id.default_credit_account_id)
        self.assertEqual(usd_aml.credit, 2000)  # agreed amount
        self.assertEqual(usd_aml.amount_currency, -100)  # payment amount
        mxn_aml = transfer.move_line_ids.filtered(
            lambda m: m.account_id ==
            transfer.destination_journal_id.default_debit_account_id)
        self.assertEqual(mxn_aml.debit, 2000)  # agreed amount
        self.assertEqual(mxn_aml.amount_currency, 0.0)

    def test_transfer_mxn_usd(self):
        transfer = self.create_internal_transfer(
            self.currency_mxn, self.bank_journal_mxn,
            self.bank_journal_usd, 1000)
        ctx = {'active_model': self.payment_model._name,
               'active_ids': transfer.ids}
        wizard = self.wizard_model.with_context(ctx).create(
            {'agreed_amount': 50, 'currency_id': self.currency_usd.id})
        wizard.apply()
        usd_aml = transfer.move_line_ids.filtered(
            lambda m: m.account_id ==
            transfer.destination_journal_id.default_credit_account_id)
        self.assertEqual(usd_aml.debit, 1000)  # payment amount
        self.assertEqual(usd_aml.amount_currency, 50)  # payment amount
        mxn_aml = transfer.move_line_ids.filtered(
            lambda m: m.account_id ==
            transfer.journal_id.default_debit_account_id)
        self.assertEqual(mxn_aml.credit, 1000)
        self.assertEqual(mxn_aml.amount_currency, 0.0)
