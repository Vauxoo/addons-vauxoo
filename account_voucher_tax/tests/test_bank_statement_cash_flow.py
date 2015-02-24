from openerp.addons.account_voucher_tax.tests.common import TestTaxCommon
import time


class TestCashFlowTaxCustomer(TestTaxCommon):

    def setUp(self):
        super(TestCashFlowTaxCustomer, self).setUp()

    def test_cf_iva_16_customer(self):
        cr, uid = self.cr, self.uid

        # create advance
        move_line_ids = self.create_statement(
            cr, uid, None, self.partner_agrolait_id, 116,
            self.bank_journal_id, time.strftime('%Y')+'-06-01',
            self.account_receivable_id)

        for move_line in move_line_ids:
            print move_line.account_id.name
            if move_line.account_id.id == self.acc_tax16_customer:
                self.assertEquals(move_line.debit, 16)
                self.assertEquals(move_line.credit, 0.0)
                self.assertEquals(move_line.amount_residual, 16)
                continue
            if move_line.account_id.id == self.acc_tax_16_payment_customer:
                self.assertEquals(move_line.debit, 0.0)
                self.assertEquals(move_line.credit, 16)
                continue
            if move_line.account_id.id == self.account_receivable_id:
                move_line_rec_id = move_line.id
                continue

        # create invoice
        invoice_id = self.account_invoice_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.invoice_journal_id,
            'reference_type': 'none',
            'name': 'invoice to customer',
            'account_id': self.account_receivable_id,
            'type': 'out_invoice',
            'date_invoice': time.strftime('%Y')+'-06-01',
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

        for line_invoice in invoice_record.move_id.line_id:
            if line_invoice.account_id.id == self.account_receivable_id:
                move_line_inv_id = line_invoice.id
                break
        # create reconciliation with account voucher
        voucher_id = self.account_voucher_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.invoice_journal_id,
            'account_id': self.account_receivable_id,
            'date': time.strftime('%Y')+'-06-01',
            'type': 'sale',
            'amount': 0
            })
        self.account_voucher_line_model.create(cr, uid, {
            'voucher_id': voucher_id,
            'type': 'dr',
            'move_line_id': move_line_rec_id,
            'partner_id': self.partner_agrolait_id,
            'account_id': self.account_receivable_id,
            'amount': 58
            })
        self.account_voucher_line_model.create(cr, uid, {
            'voucher_id': voucher_id,
            'type': 'cr',
            'move_line_id': move_line_inv_id,
            'partner_id': self.partner_agrolait_id,
            'account_id': self.account_receivable_id,
            'amount': 58
            })

        for voucher_line in self.account_voucher_model.browse(cr, uid, voucher_id).line_ids:
            print voucher_line,"wwwwwwwwwwwwwwww"

        self.account_voucher_model.proforma_voucher(cr, uid, voucher_id, {})

        for line_invoice in invoice_record.move_id.line_id:
            if line_invoice.account_id.id == self.acc_tax16_customer:
                print line_invoice.id,"line_invoice"
                print line_invoice.amount_residual
                print line_invoice.reconcile_id
                print line_invoice.reconcile_partial_id

                self.assertEquals(move_line.debit, 16)
                self.assertEquals(move_line.credit, 0.0)
                self.assertEquals(move_line.amount_residual, 0)
                continue
