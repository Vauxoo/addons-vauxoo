# -*- coding: utf-8 -*-

from openerp.tests import common
import time


class TestTaxCommon(common.TransactionCase):

    def setUp(self):
        super(TestTaxCommon, self).setUp()
        self.account_invoice_model = self.registry('account.invoice')
        self.account_invoice_line_model = self.registry('account.invoice.line')
        self.acc_bank_stmt_model = self.registry('account.bank.statement')
        self.acc_bank_stmt_line_model = self.registry(
            'account.bank.statement.line')
        self.precision_obj = self.registry('decimal.precision')
        self.partner_agrolait_id = self.ref("base.res_partner_2")
        self.account_payable_id = self.ref("account.a_pay")
        self.account_receivable_id = self.ref("account.a_recv")
        self.product_id = self.ref("product.product_product_4")
        self.invoice_journal_id = self.ref("account.sales_journal")
        self.invoice_supplier_journal_id = self.ref("account.expenses_journal")
        self.bank_journal_id = self.ref("account.bank_journal")
        self.bank_journal_usd_id = self.ref("account.bank_journal_usd")
        self.currency_usd_id = self.ref("base.USD")
        self.acc_loss_tax = self.ref("account.income_fx_expense")
        self.acc_gain_tax = self.ref("account.income_fx_income")
        self.company_id = self.ref("base.main_company")
        # set expense_currency_exchange_account_id and
        # income_currency_exchange_account_id to a random account
        self.registry("res.company").write(
            self.cr, self.uid, [self.company_id],
            {'expense_currency_exchange_account_id': self.acc_loss_tax,
             'income_currency_exchange_account_id': self.acc_gain_tax})

        # Data to tax
        self.tax_16 = self.ref(
            "account_voucher_tax.account_voucher_tax_purchase_iva16")
        self.tax_16_customer = self.ref(
            "account_voucher_tax.account_voucher_tax_sale_ova16")
        self.tax_ret = self.ref(
            "account_voucher_tax.account_voucher_tax_purchase_iva1067_retencion_iva")

        # Data account to tax
        self.acc_tax16 = self.ref(
            "account_voucher_tax.account_iva_voucher_16")
        self.acc_tax16_customer = self.ref(
            "account_voucher_tax.account_ova_voucher_16")
        self.acc_ret1067 = self.ref(
            "account_voucher_tax.account_iva_voucher_retencion_iva_1067")

        self.acc_tax_16_payment = self.ref(
            "account_voucher_tax.account_iva_voucher")
        self.acc_tax_16_payment_customer = self.ref(
            "account_voucher_tax.account_ova_voucher")
        self.acc_ret1067_payment = self.ref(
            "account_voucher_tax.account_iva_voucher1067_retencion_iva")

    def create_statement(self, cr, uid, line_invoice, partner, amount, journal,
                         date_bank=None):
        bank_stmt_id = self.acc_bank_stmt_model.create(cr, uid, {
            'journal_id': journal,
            'date': date_bank or time.strftime('%Y')+'-07-01',
        })

        bank_stmt_line_id = self.acc_bank_stmt_line_model.create(cr, uid, {
            'name': 'payment',
            'statement_id': bank_stmt_id,
            'partner_id': partner,
            'amount': amount,
            'date': date_bank or time.strftime('%Y')+'-07-01'})

        self.acc_bank_stmt_line_model.process_reconciliation(
            cr, uid, bank_stmt_line_id, [{
                'counterpart_move_line_id': line_invoice.id,
                'credit': amount > 0 and amount or 0,
                'debit': amount < 0 and amount*-1 or 0,
                'name': line_invoice.name}])

        move_line_ids_complete = self.acc_bank_stmt_model.browse(
            cr, uid, bank_stmt_id).move_line_ids

        return move_line_ids_complete
