from openerp.addons.account_voucher_tax.tests.common import TestTaxCommon
import time


class TestPaymentTaxCustomer(TestTaxCommon):

    def setUp(self):
        super(TestPaymentTaxCustomer, self).setUp()

    def test_iva_16_customer(self):
        cr, uid = self.cr, self.uid
        invoice_id = self.account_invoice_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'reference_type': 'none',
            'name': 'invoice to customer',
            'account_id': self.account_receivable_id,
            'type': 'out_invoice',
            'date_invoice': time.strftime('%Y')+'-07-01',
            })
        self.account_invoice_line_model.create(cr, uid, {
            'product_id': self.product_id,
            'quantity': 1,
            'price_unit': 100,
            'invoice_line_tax_id': [(6, 0, [self.tax_16_customer])],
            'invoice_id': invoice_id,
            'name': 'product that cost 100'})

        # validate invoice
        self.registry('account.invoice').signal_workflow(
            cr, uid, [invoice_id], 'invoice_open')
        invoice_record = self.account_invoice_model.browse(
            cr, uid, [invoice_id])

        # we search aml with account payable
        for l in invoice_record.move_id.line_id:
            if l.account_id.id == self.account_receivable_id:
                line_id = l
                break

        # create payment by half
        move_line_ids = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, 116,
            self.bank_journal_id)

        for move_line in move_line_ids:
            if move_line.account_id.id == self.acc_tax16_customer:
                self.assertEquals(move_line.debit, 16)
                self.assertEquals(move_line.credit, 0.0)
                self.assertEquals(move_line.amount_residual, 0)
                continue
            if move_line.account_id.id == self.acc_tax_16_payment_customer:
                self.assertEquals(move_line.debit, 0.0)
                self.assertEquals(move_line.credit, 16)
                continue
