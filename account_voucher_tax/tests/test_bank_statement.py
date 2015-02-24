from openerp.addons.account_voucher_tax.tests.common import TestTaxCommon
import time


class TestPaymentTax(TestTaxCommon):

    def setUp(self):
        super(TestPaymentTax, self).setUp()

    def test_iva_16_supplier(self):
        cr, uid = self.cr, self.uid
        invoice_id = self.account_invoice_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.invoice_supplier_journal_id,
            'reference_type': 'none',
            'name': 'invoice to supplier',
            'account_id': self.account_payable_id,
            'type': 'in_invoice',
            'date_invoice': time.strftime('%Y')+'-07-01',
            'check_total': 116
            })
        self.account_invoice_line_model.create(cr, uid, {
            'product_id': self.product_id,
            'quantity': 1,
            'price_unit': 100,
            'invoice_line_tax_id': [(6, 0, [self.tax_16])],
            'invoice_id': invoice_id,
            'name': 'product that cost 100'})

        # validate invoice
        self.registry('account.invoice').signal_workflow(
            cr, uid, [invoice_id], 'invoice_open')
        invoice_record = self.account_invoice_model.browse(
            cr, uid, [invoice_id])

        # we search aml with account payable
        for line_invoice in invoice_record.move_id.line_id:
            if line_invoice.account_id.id == self.account_payable_id:
                line_id = line_invoice
                break

        # create payment by half
        move_line_ids = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, -58,
            self.bank_journal_id)

        self.assertEquals(len(move_line_ids), 4)
        for move_line in move_line_ids:
            if move_line.account_id.id == self.acc_tax16:
                self.assertEquals(move_line.debit, 0.0)
                self.assertEquals(move_line.credit, 8)
                self.assertEquals(move_line.amount_residual, -8)
                continue
            if move_line.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(move_line.debit, 8)
                self.assertEquals(move_line.credit, 0.0)
                continue

        # create payment complete

        move_line_ids_complete = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, -58,
            self.bank_journal_id)

        for move_line_complete in move_line_ids_complete:
            if move_line_complete.account_id.id == self.acc_tax16:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(move_line_complete.credit, 8)
                self.assertEquals(move_line_complete.amount_residual, 0.0)
                continue
            if move_line_complete.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(move_line_complete.debit, 8)
                self.assertEquals(move_line_complete.credit, 0.0)
                continue

    def test_iva_16_ret_supplier(self):
        cr, uid = self.cr, self.uid
        invoice_id = self.account_invoice_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.invoice_supplier_journal_id,
            'reference_type': 'none',
            'name': 'invoice to supplier',
            'account_id': self.account_payable_id,
            'type': 'in_invoice',
            'date_invoice': time.strftime('%Y')+'-07-01',
            'check_total': 105.33
            })
        self.account_invoice_line_model.create(cr, uid, {
            'product_id': self.product_id,
            'quantity': 1,
            'price_unit': 100,
            'invoice_line_tax_id': [(6, 0, [self.tax_16, self.tax_ret])],
            'invoice_id': invoice_id,
            'name': 'product that cost 100'})

        # validate invoice
        self.registry('account.invoice').signal_workflow(
            cr, uid, [invoice_id], 'invoice_open')
        invoice_record = self.account_invoice_model.browse(
            cr, uid, [invoice_id])

        # we search aml with account payable
        for line_invoice in invoice_record.move_id.line_id:
            if line_invoice.account_id.id == self.account_payable_id:
                line_id = line_invoice
                break

        # create payment
        move_line_ids_complete = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, -105.33,
            self.bank_journal_id)

        for move_line_complete in move_line_ids_complete:
            if move_line_complete.account_id.id == self.acc_tax16:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(move_line_complete.credit, 5.33)
                self.assertEquals(move_line_complete.amount_residual, -10.67)
                continue
            if move_line_complete.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(move_line_complete.debit, 5.33)
                self.assertEquals(move_line_complete.credit, 0.0)
                continue

            # retention tax validation
            if move_line_complete.account_id.id == self.acc_ret1067:
                self.assertEquals(move_line_complete.debit, 10.67)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(move_line_complete.amount_residual, 0.0)
                continue
            if move_line_complete.account_id.id == self.acc_ret1067_payment:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(move_line_complete.credit, 10.67)
                continue

    def test_iva_16_currency_supplier(self):
        cr, uid = self.cr, self.uid
        invoice_id = self.account_invoice_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.invoice_supplier_journal_id,
            'reference_type': 'none',
            'name': 'invoice to supplier',
            'account_id': self.account_payable_id,
            'type': 'in_invoice',
            'date_invoice': time.strftime('%Y')+'-06-01',
            'currency_id': self.currency_usd_id,
            'check_total': 116
            })
        self.account_invoice_line_model.create(cr, uid, {
            'product_id': self.product_id,
            'quantity': 1,
            'price_unit': 100,
            'invoice_line_tax_id': [(6, 0, [self.tax_16])],
            'invoice_id': invoice_id,
            'name': 'product that cost 100'})

        # validate invoice
        self.registry('account.invoice').signal_workflow(
            cr, uid, [invoice_id], 'invoice_open')
        invoice_record = self.account_invoice_model.browse(
            cr, uid, [invoice_id])

        # we search aml with account payable
        for line_invoice in invoice_record.move_id.line_id:
            if line_invoice.account_id.id == self.account_payable_id:
                line_id = line_invoice
                break

        # create payment complete

        move_line_ids_complete = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, -116,
            self.bank_journal_usd_id, time.strftime('%Y')+'-06-30')

        checked_line = 0
        for move_line_complete in move_line_ids_complete:
            if move_line_complete.account_id.id == self.acc_tax16 and\
                    move_line_complete.amount_currency == 0:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(move_line_complete.credit, 2)
                self.assertEquals(move_line_complete.amount_residual, 0.0)
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_tax16 and\
                    move_line_complete.amount_currency:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(move_line_complete.credit, 10.47)
                self.assertEquals(move_line_complete.amount_residual, 0.0)
                self.assertEquals(move_line_complete.amount_currency, -16)
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(move_line_complete.debit, 10.47)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(move_line_complete.amount_currency, 16)
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_loss_tax:
                self.assertEquals(move_line_complete.debit, 2)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(move_line_complete.amount_currency, 0)
                checked_line += 1
                continue
        self.assertEquals(checked_line, 4)
