from openerp.addons.account_voucher_tax.tests.common import TestTaxCommon
import time


class TestPaymentTaxCustomer(TestTaxCommon):

    def setUp(self):
        super(TestPaymentTaxCustomer, self).setUp()

    def test_iva_16_customer(self):
        cr, uid = self.cr, self.uid
        invoice_id = self.account_invoice_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.invoice_journal_id,
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
        for line_invoice in invoice_record.move_id.line_id:
            if line_invoice.account_id.id == self.account_receivable_id:
                line_id = line_invoice
                break

        # create payment complete
        move_line_ids = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, 116,
            self.bank_journal_id)

        for move_line in move_line_ids:
            if move_line.account_id.id == self.acc_tax16_customer:
                self.assertEquals(move_line.debit, 16)
                self.assertEquals(move_line.credit, 0.0)
                self.assertEquals(move_line.amount_residual, 0)
                self.assertTrue(move_line.reconcile_id,
                                "Reconcile should be created.")
                continue
            if move_line.account_id.id == self.acc_tax_16_payment_customer:
                self.assertEquals(move_line.debit, 0.0)
                self.assertEquals(move_line.credit, 16)
                continue

    def test_iva_16_currency_customer(self):
        cr, uid = self.cr, self.uid
        invoice_id = self.account_invoice_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.invoice_journal_id,
            'reference_type': 'none',
            'name': 'invoice to customer',
            'account_id': self.account_receivable_id,
            'type': 'out_invoice',
            'date_invoice': time.strftime('%Y')+'-06-01',
            'currency_id': self.currency_usd_id
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
        for line_invoice in invoice_record.move_id.line_id:
            if line_invoice.account_id.id == self.account_receivable_id:
                line_id = line_invoice
                break

        # create payment half
        move_line_ids = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, 58,
            self.bank_journal_usd_id, time.strftime('%Y')+'-06-01')

        for move_line in move_line_ids:
            if move_line.account_id.id == self.acc_tax16_customer:
                self.assertEquals(move_line.debit, 6.23)
                self.assertEquals(move_line.credit, 0.0)
                self.assertEquals(move_line.amount_residual, -6.24)
                self.assertEquals(move_line.amount_currency, 8.0)
                self.assertTrue(move_line.reconcile_partial_id,
                                "Partial Reconcile should be created.")
                continue
            if move_line.account_id.id == self.acc_tax_16_payment_customer:
                self.assertEquals(move_line.debit, 0.0)
                self.assertEquals(move_line.credit, 6.23)
                self.assertEquals(move_line.amount_currency, -8)
                continue

        # create payment complete
        move_line_ids_complete = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, 58,
            self.bank_journal_usd_id, time.strftime('%Y')+'-06-30')

        checked_line = 0
        for move_line_complete in move_line_ids_complete:
            if move_line_complete.account_id.id ==\
                    self.acc_tax16_customer and\
                    move_line_complete.amount_currency:
                self.assertEquals(move_line_complete.debit, 5.23)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(move_line_complete.amount_residual, 0)
                self.assertEquals(move_line_complete.amount_currency, 8.0)
                self.assertTrue(move_line_complete.reconcile_id,
                                "Reconcile should be created.")
                checked_line += 1
                continue
            if move_line_complete.account_id.id ==\
                    self.acc_tax_16_payment_customer:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(move_line_complete.credit, 5.23)
                self.assertEquals(move_line_complete.amount_currency, -8)
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_tax16_customer:
                self.assertEquals(move_line_complete.debit, 1.01)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(move_line_complete.amount_residual, 0)
                self.assertEquals(move_line_complete.amount_currency, 0)
                self.assertTrue(move_line_complete.reconcile_id,
                                "Reconcile should be created.")
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_gain_tax:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(move_line_complete.credit, 1.01)
                self.assertEquals(move_line_complete.amount_currency, 0)
                checked_line += 1
                continue

        self.assertEquals(checked_line, 4)

    def test_iva_16_currency_customer_almost_complete(self):
        cr, uid = self.cr, self.uid
        invoice_id = self.account_invoice_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.invoice_journal_id,
            'reference_type': 'none',
            'name': 'invoice to customer',
            'account_id': self.account_receivable_id,
            'type': 'out_invoice',
            'date_invoice': time.strftime('%Y')+'-06-30',
            'currency_id': self.currency_usd_id
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
        for line_invoice in invoice_record.move_id.line_id:
            if line_invoice.account_id.id == self.account_receivable_id:
                line_id = line_invoice
                break

        # create payment almost complete by 115
        move_line_ids = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, 115,
            self.bank_journal_usd_id, time.strftime('%Y')+'-06-01')

        for move_line in move_line_ids:
            if move_line.account_id.id == self.acc_tax16_customer:
                self.assertEquals(move_line.debit, 12.36)
                self.assertEquals(move_line.credit, 0.0)
                self.assertEquals(round(move_line.amount_residual, 2), 1.89)
                self.assertEquals(round(move_line.amount_currency, 2), 15.86)
                self.assertTrue(move_line.reconcile_partial_id,
                                "Partial Reconcile should be created.")
                continue
            if move_line.account_id.id == self.acc_tax_16_payment_customer:
                self.assertEquals(move_line.debit, 0.0)
                self.assertEquals(move_line.credit, 12.36)
                self.assertEquals(round(move_line.amount_currency, 2), -15.86)
                continue

        # create payment complete
        move_line_ids_complete = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, 1,
            self.bank_journal_usd_id, time.strftime('%Y')+'-06-30')

        checked_line = 0
        for move_line_complete in move_line_ids_complete:
            if move_line_complete.account_id.id ==\
                    self.acc_tax16_customer and\
                    move_line_complete.amount_currency:
                self.assertEquals(move_line_complete.debit, 0.09)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(move_line_complete.amount_residual, 0)
                self.assertEquals(move_line_complete.amount_currency, 0.14)
                self.assertTrue(move_line_complete.reconcile_id,
                                "Reconcile should be created.")
                checked_line += 1
                continue
            if move_line_complete.account_id.id ==\
                    self.acc_tax_16_payment_customer:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(move_line_complete.credit, 0.09)
                self.assertEquals(move_line_complete.amount_currency, -0.14)
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_tax16_customer:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(move_line_complete.credit, 1.98)
                self.assertEquals(move_line_complete.amount_residual, 0)
                self.assertEquals(move_line_complete.amount_currency, 0)
                self.assertTrue(move_line_complete.reconcile_id,
                                "Partial Reconcile should be created.")
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_loss_tax:
                self.assertEquals(move_line_complete.debit, 1.98)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(move_line_complete.amount_currency, 0)
                checked_line += 1
                continue

        self.assertEquals(checked_line, 4)
