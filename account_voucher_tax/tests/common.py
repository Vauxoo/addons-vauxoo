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
        self.partner_agrolait_id = self.registry(
            "ir.model.data").get_object_reference(
            self.cr, self.uid, "base", "res_partner_2")[1]
        self.account_payable_id = self.registry(
            "ir.model.data").get_object_reference(
            self.cr, self.uid, "account", "a_pay")[1]
        self.account_receivable_id = self.registry(
            "ir.model.data").get_object_reference(
            self.cr, self.uid, "account", "a_recv")[1]
        self.product_id = self.registry(
            "ir.model.data").get_object_reference(
            self.cr, self.uid, "product", "product_product_4")[1]
        self.bank_journal_id = self.registry(
            "ir.model.data").get_object_reference(
            self.cr, self.uid, "account", "bank_journal")[1]
        self.bank_journal_usd_id = self.registry(
            "ir.model.data").get_object_reference(
            self.cr, self.uid, "account", "bank_journal_usd")[1]
        self.currency_usd_id = self.registry(
            "ir.model.data").get_object_reference(
            self.cr, self.uid, "base", "USD")[1]
        self.acc_loss_tax = self.registry(
            "ir.model.data").get_object_reference(
            self.cr, self.uid, "account", "income_fx_expense")[1]
        self.acc_gain_tax = self.registry(
            "ir.model.data").get_object_reference(
            self.cr, self.uid, "account", "income_fx_income")[1]

        # Data to tax
        self.tax_16 = self.registry(
            "ir.model.data").get_object_reference(
            self.cr, self.uid, "account_voucher_tax",
            "account_voucher_tax_purchase_iva16")[1]
        self.tax_16_customer = self.registry(
            "ir.model.data").get_object_reference(
            self.cr, self.uid, "account_voucher_tax",
            "account_voucher_tax_sale_ova16")[1]
        self.tax_ret = self.registry(
            "ir.model.data").get_object_reference(
            self.cr, self.uid, "account_voucher_tax",
            "account_voucher_tax_purchase_iva1067_retencion_iva")[1]

        # Data account to tax
        self.acc_tax16 = self.registry(
            "ir.model.data").get_object_reference(
            self.cr, self.uid, "account_voucher_tax",
            "account_iva_voucher_16")[1]
        self.acc_tax16_customer = self.registry(
            "ir.model.data").get_object_reference(
            self.cr, self.uid, "account_voucher_tax",
            "account_ova_voucher_16")[1]
        self.acc_ret1067 = self.registry(
            "ir.model.data").get_object_reference(
            self.cr, self.uid, "account_voucher_tax",
            "account_iva_voucher_retencion_iva_1067")[1]

        self.acc_tax_16_payment = self.registry(
            "ir.model.data").get_object_reference(
            self.cr, self.uid, "account_voucher_tax",
            "account_iva_voucher")[1]
        self.acc_tax_16_payment_customer = self.registry(
            "ir.model.data").get_object_reference(
            self.cr, self.uid, "account_voucher_tax",
            "account_ova_voucher")[1]
        self.acc_ret1067_payment = self.registry(
            "ir.model.data").get_object_reference(
            self.cr, self.uid, "account_voucher_tax",
            "account_iva_voucher1067_retencion_iva")[1]

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
