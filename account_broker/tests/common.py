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
        _, self.account_vou = imd_model.get_object_reference(
            cr, uid, "account", "cash")
        _, self.account_inv = imd_model.get_object_reference(
            cr, uid, "account", "a_pay")
        _, self.partner_id = imd_model.get_object_reference(
            cr, uid, "account_broker", "res_partner_supplier_broker")
        _, self.company_id = imd_model.get_object_reference(
            cr, uid, "base", "main_company")
        _, self.currency_id = imd_model.get_object_reference(
            cr, uid, "base", "MXN")
        _, self.journal_inv_id = imd_model.get_object_reference(
            cr, uid, "account", "expenses_journal")
        _, self.journal_vou_id = imd_model.get_object_reference(
            cr, uid, "account", "bank_journal")
        _, self.acc_line_id = imd_model.get_object_reference(
            cr, uid, "account", "a_expense")
        _, self.prod_line1 = imd_model.get_object_reference(
            cr, uid, "account_broker", "product_product_broker_payment")
        _, self.prod_line2 = imd_model.get_object_reference(
            cr, uid, "product", "product_product_39")
        _, self.tax_brok16_id = imd_model.get_object_reference(
            cr, uid, "account_broker", "account_tax_purchase_iva16_broker")
        _, self.tax_16_id = imd_model.get_object_reference(
            cr, uid, "account_voucher_tax",
            "account_voucher_tax_purchase_iva16")
        _, self.tax_inv_2_id = imd_model.get_object_reference(
            cr, uid, "account", "test_invoice_1")
        _, self.account_receivable_id = imd_model.get_object_reference(
            cr, uid, "account", "a_recv")
        _, self.account_voucher_tax_16 = imd_model.get_object_reference(
            cr, uid, "account_voucher_tax", "account_iva_voucher_16")

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
