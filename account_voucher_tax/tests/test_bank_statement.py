from openerp.addons.account_voucher_tax.tests.common import TestTaxCommon
from openerp.tools import float_compare
import time


class TestPaymentTax(TestTaxCommon):
    """
        These Tests were made based on this document,
        https://docs.google.com/a/vauxoo.com/spreadsheets/d/1O82bBb-mySbpH7SiY1KQILsIIRMgcO5E0ddNuCGC0N8/edit#gid=0
        to test the successful creation of taxes efectivamete pagado / cobrado
        of supplier in payments by bank statement
    """

    def setUp(self):
        super(TestPaymentTax, self).setUp()

    def test_iva_16_supplier(self):
        """
            Tests Supplier with tax 16% and two payments
        """
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
                self.assertTrue(move_line.reconcile_partial_id,
                                "Partial Reconcile should be created.")
                continue
            if move_line.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(move_line.debit, 8)
                self.assertEquals(move_line.credit, 0.0)
                self.assertEquals(move_line.amount_base, 50.0)
                self.assertNotEqual(move_line.tax_id_secondary, False)
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
                self.assertTrue(move_line_complete.reconcile_id,
                                "Reconcile should be created.")
                continue
            if move_line_complete.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(move_line_complete.debit, 8)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(move_line_complete.amount_base, 50.0)
                self.assertNotEqual(move_line_complete.tax_id_secondary, False)
                continue

    def test_iva_16_ret_supplier(self):
        """
            Tests Supplier with two taxes IVA 16%
            and Retention 10.67% with one payment
        """
        cr, uid = self.cr, self.uid
        precision = self.precision_obj.precision_get(cr, uid, 'Account')
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
                self.assertEquals(float_compare(
                    move_line_complete.credit, 5.33,
                    precision_digits=precision), 0)
                self.assertEquals(float_compare(
                    move_line_complete.amount_residual, -10.67,
                    precision_digits=precision), 0)
                self.assertTrue(move_line_complete.reconcile_partial_id,
                                "Partial Reconcile should be created.")
                continue
            if move_line_complete.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(float_compare(
                    move_line_complete.debit, 5.33,
                    precision_digits=precision), 0)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(float_compare(
                    move_line_complete.amount_base, 33.31,
                    precision_digits=precision), 0)
                self.assertNotEqual(move_line_complete.tax_id_secondary, False)
                continue

            # retention tax validation
            if move_line_complete.account_id.id == self.acc_ret1067:
                self.assertEquals(float_compare(
                    move_line_complete.debit, 10.67,
                    precision_digits=precision), 0)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(move_line_complete.amount_residual, 0.0)
                self.assertTrue(move_line_complete.reconcile_id,
                                "Reconcile should be created.")
                continue
            if move_line_complete.account_id.id == self.acc_ret1067_payment:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(float_compare(
                    move_line_complete.credit, 10.67,
                    precision_digits=precision), 0)
                continue

    def test_iva_16_currency_supplier(self):
        """
            Tests Supplier with currency USD and tax 16% with two payments
        """
        cr, uid = self.cr, self.uid
        precision = self.precision_obj.precision_get(cr, uid, 'Account')
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

        # create payment half

        move_line_ids_complete = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, -60,
            self.bank_journal_usd_id, time.strftime('%Y')+'-06-01')
        for move_line in move_line_ids_complete:
            if move_line.account_id.id == self.acc_tax16 and\
                    move_line.amount_currency:
                self.assertEquals(move_line.debit, 0.0)
                self.assertEquals(float_compare(
                    move_line.credit, 6.45,
                    precision_digits=precision), 0)
                self.assertEquals(float_compare(
                    move_line.amount_residual, -6.02,
                    precision_digits=precision), 0)
                self.assertEquals(float_compare(
                    move_line.amount_currency, -8.28,
                    precision_digits=precision), 0)
                self.assertTrue(move_line.reconcile_partial_id,
                                "Partial Reconcile should be created.")
                continue
            if move_line.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(float_compare(
                    move_line.debit, 6.45,
                    precision_digits=precision), 0)
                self.assertEquals(move_line.credit, 0.0)
                self.assertEquals(float_compare(
                    move_line.amount_currency, 8.28,
                    precision_digits=precision), 0)
                self.assertEquals(float_compare(
                    move_line.amount_base, 40.30,
                    precision_digits=precision), 0)
                self.assertNotEqual(move_line.tax_id_secondary, False)
                continue

        # create payment complete

        move_line_ids_complete = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, -56,
            self.bank_journal_usd_id, time.strftime('%Y')+'-06-30')

        checked_line = 0
        for move_line_complete in move_line_ids_complete:
            if move_line_complete.account_id.id == self.acc_tax16 and\
                    move_line_complete.amount_currency == 0:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(float_compare(
                    move_line_complete.credit, 0.97,
                    precision_digits=precision), 0)
                self.assertEquals(move_line_complete.amount_residual, 0.0)
                self.assertTrue(move_line_complete.reconcile_id,
                                "Reconcile should be created.")
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_tax16 and\
                    move_line_complete.amount_currency:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(float_compare(
                    move_line_complete.credit, 5.05,
                    precision_digits=precision), 0)
                self.assertEquals(move_line_complete.amount_residual, 0.0)
                self.assertEquals(float_compare(
                    move_line_complete.amount_currency, -7.72,
                    precision_digits=precision), 0)
                self.assertTrue(move_line_complete.reconcile_id,
                                "Reconcile should be created.")
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(float_compare(
                    move_line_complete.debit, 5.05,
                    precision_digits=precision), 0)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(float_compare(
                    move_line_complete.amount_currency, 7.72,
                    precision_digits=precision), 0)
                self.assertEquals(float_compare(
                    move_line_complete.amount_base, 31.58,
                    precision_digits=precision), 0)
                self.assertNotEqual(move_line_complete.tax_id_secondary, False)
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_loss_tax:
                self.assertEquals(float_compare(
                    move_line_complete.debit, 0.97,
                    precision_digits=precision), 0)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(move_line_complete.amount_currency, 0)
                checked_line += 1
                continue
        self.assertEquals(checked_line, 4)

    def test_iva_16_currency_supplier_almost_complete(self):
        """
            Tests Supplier with currency USD and tax 16% and two payments
            First payment almost complete and exchange rate
                greater then invoice
            Second payment with exchange rate same that invoice
        """
        cr, uid = self.cr, self.uid
        precision = self.precision_obj.precision_get(cr, uid, 'Account')
        invoice_id = self.account_invoice_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.invoice_supplier_journal_id,
            'reference_type': 'none',
            'name': 'invoice to supplier',
            'account_id': self.account_payable_id,
            'type': 'in_invoice',
            'date_invoice': time.strftime('%Y')+'-06-30',
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

        # create payment almost complete

        move_line_ids_complete = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, -115,
            self.bank_journal_usd_id, time.strftime('%Y')+'-06-01')
        for move_line in move_line_ids_complete:
            if move_line.account_id.id == self.acc_tax16 and\
                    move_line.amount_currency:
                self.assertEquals(move_line.debit, 0.0)
                self.assertEquals(float_compare(
                    move_line.credit, 12.36,
                    precision_digits=precision), 0)
                self.assertEquals(float_compare(
                    move_line.amount_residual, 1.89,
                    precision_digits=precision), 0)
                self.assertEquals(float_compare(
                    move_line.amount_currency, -15.86,
                    precision_digits=precision), 0)
                self.assertTrue(move_line.reconcile_partial_id,
                                "Partial Reconcile should be created.")
                continue
            if move_line.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(float_compare(
                    move_line.debit, 12.36,
                    precision_digits=precision), 0)
                self.assertEquals(move_line.credit, 0.0)
                self.assertEquals(float_compare(
                    move_line.amount_currency, 15.86,
                    precision_digits=precision), 0)
                self.assertEquals(float_compare(
                    move_line.amount_base, 77.25,
                    precision_digits=precision), 0)
                self.assertNotEqual(move_line.tax_id_secondary, False)
                continue

        # create payment complete

        move_line_ids_complete = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, -1,
            self.bank_journal_usd_id, time.strftime('%Y')+'-06-30')

        checked_line = 0
        for move_line_complete in move_line_ids_complete:
            if move_line_complete.account_id.id == self.acc_tax16 and\
                    move_line_complete.amount_currency == 0:
                self.assertEquals(float_compare(
                    move_line_complete.debit, 1.98,
                    precision_digits=precision), 0)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(move_line_complete.amount_residual, 0.0)
                self.assertTrue(move_line_complete.reconcile_id,
                                "Reconcile should be created.")
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_tax16 and\
                    move_line_complete.amount_currency:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(float_compare(
                    move_line_complete.credit, 0.09,
                    precision_digits=precision), 0)
                self.assertEquals(move_line_complete.amount_residual, 0.0)
                self.assertEquals(float_compare(
                    move_line_complete.amount_currency, -0.14,
                    precision_digits=precision), 0)
                self.assertTrue(move_line_complete.reconcile_id,
                                "Reconcile should be created.")
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(float_compare(
                    move_line_complete.debit, 0.09,
                    precision_digits=precision), 0)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(float_compare(
                    move_line_complete.amount_currency, 0.14,
                    precision_digits=precision), 0)
                self.assertEquals(float_compare(
                    move_line_complete.amount_base, 0.56,
                    precision_digits=precision), 0)
                self.assertNotEqual(move_line_complete.tax_id_secondary, False)
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_gain_tax:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(float_compare(
                    move_line_complete.credit, 1.98,
                    precision_digits=precision), 0)
                self.assertEquals(move_line_complete.amount_currency, 0)
                checked_line += 1
                continue
        self.assertEquals(checked_line, 4)
