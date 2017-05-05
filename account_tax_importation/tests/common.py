# coding: utf-8
from openerp.tests import common
import time


class TestTaxCommon(common.TransactionCase):

    def setUp(self):
        super(TestTaxCommon, self).setUp()
        cr, uid = self.cr, self.uid
        imd_model = self.registry("ir.model.data")
        self.inv_model = self.registry('account.invoice')
        self.voucher_model = self.registry('account.voucher')
        self.voucher_model_line = self.registry('account.voucher.line')
        self.acc_bank_stmt_model = self.registry('account.bank.statement')
        self.acc_bank_stmt_line_model = self.registry(
            'account.bank.statement.line')
        self.account_vou = self.ref("account.cash")
        self.account_inv = self.ref("account.a_pay")
        self.partner_id = self.ref(
            "account_tax_importation.res_partner_supplier_broker")
        self.company_id = self.ref("base.main_company")
        self.journal_inv_id = self.ref("account.expenses_journal")
        self.journal_vou_id = self.ref("account.bank_journal")
        self.acc_line_id = self.ref("account.a_expense")
        self.prod_line1 = self.ref(
            "account_tax_importation.product_product_broker_payment")
        self.prod_line2 = self.ref("product.product_product_39")
        self.tax_brok16_id = self.ref(
            "account_tax_importation.account_tax_purchase_iva16_broker")
        self.tax_16_id = self.ref(
            "account_voucher_tax.account_voucher_tax_purchase_iva16")
        self.tax_inv_2_id = self.ref("account.test_invoice_1")
        self.account_receivable_id = self.ref("account.a_recv")
        self.account_voucher_tax_16 = self.ref(
            "account_voucher_tax.account_iva_voucher_16")

    def create_statement(self, cr, uid, line_invoice, partner, amount, journal,
                         date_bank=None):
        bank_stmt_id = self.acc_bank_stmt_model.create(cr, uid, {
            'journal_id': journal,
            'date': date_bank or time.strftime('%Y') + '-07-01',
        })

        bank_stmt_line_id = self.acc_bank_stmt_line_model.create(cr, uid, {
            'name': 'payment',
            'statement_id': bank_stmt_id,
            'partner_id': partner,
            'amount': amount,
            'date': date_bank or time.strftime('%Y') + '-07-01'})

        self.acc_bank_stmt_line_model.process_reconciliation(
            cr, uid, bank_stmt_line_id, [{
                'counterpart_move_line_id': line_invoice.id,
                'credit': amount > 0 and amount or 0,
                'debit': amount < 0 and amount * -1 or 0,
                'name': line_invoice.name}])

        move_line_ids_complete = self.acc_bank_stmt_model.browse(
            cr, uid, bank_stmt_id).move_line_ids

        return move_line_ids_complete

    def create_invoice(self, cr, uid, context=None):
        inv_id = self.inv_model.create(cr, uid, dict(
            account_id=self.account_inv,
            partner_id=self.partner_id,
            check_total=7694.20,
            company_id=self.company_id,
            journal_id=self.journal_inv_id,
            reference_type='none',
            invoice_line=[(0, 0, {
                'name': '[Importation]Product for importation',
                'account_id': self.acc_line_id,
                'price_unit': 1000.0,
                'product_id': self.prod_line1,
                'quantity': 0,
                'invoice_line_tax_id': [(6, 0, [self.tax_brok16_id])],
                'invoice_broker_id': self.tax_inv_2_id
            }), (0, 0, {
                'name': '[Importation]Product for importation',
                'account_id': self.acc_line_id,
                'price_unit': 1299.0,
                'product_id': self.prod_line2,
                'quantity': 5,
                'invoice_line_tax_id': [(6, 0, [self.tax_16_id])]
            })]
        ), context=context)
        return inv_id
