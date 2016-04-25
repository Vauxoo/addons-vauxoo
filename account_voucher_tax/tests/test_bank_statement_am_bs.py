# coding: utf-8
from openerp.addons.account_voucher_tax.tests.common import TestTaxCommon
from openerp.tools import float_compare
import time


class TestPaymentTax(TestTaxCommon):
    """These Tests were made based on this document,
        https://docs.google.com/a/vauxoo.com/spreadsheets/d/1O82bBb-mySbpH7SiY1KQILsIIRMgcO5E0ddNuCGC0N8/edit#gid=0
        to test the successful creation of taxes Efectivaly paid and received.
        of supplier in payments by bank statement
    """

    def setUp(self):
        super(TestPaymentTax, self).setUp()
        self.precision_obj = self.registry('decimal.precision')

    def test_iva_16_supplier(self):
        """Tests Supplier with tax 16% and two payments
        """
        cr, uid = self.cr, self.uid
        invoice_id = self.create_invoice_supplier(
            cr, uid, 116, [self.tax_16], time.strftime('%Y') + '-07-01')

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
            if move_line.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(move_line.amount_base, 50.0)
                self.assertNotEqual(move_line.tax_id_secondary, False)
                continue

        # create payment complete

        move_line_ids_complete = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, -58,
            self.bank_journal_id)

        for move_line_complete in move_line_ids_complete:
            if move_line_complete.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(move_line_complete.amount_base, 50.0)
                self.assertNotEqual(move_line_complete.tax_id_secondary, False)
                continue

    def test_iva_16_ret_supplier(self):
        """Tests Supplier with two taxes IVA 16%
            and Retention 10.67% with one payment
        """
        cr, uid = self.cr, self.uid
        precision = self.precision_obj.precision_get(cr, uid, 'Account')
        invoice_id = self.create_invoice_supplier(
            cr, uid, 105.33, [self.tax_16, self.tax_ret],
            time.strftime('%Y') + '-07-01')

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
            if move_line_complete.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(float_compare(
                    move_line_complete.amount_base, 33.31,
                    precision_digits=precision), 0)
                self.assertNotEqual(move_line_complete.tax_id_secondary, False)
                continue
            elif move_line_complete.account_id.id == self.acc_ret1067_payment:
                self.assertEquals(float_compare(
                    move_line_complete.amount_base, 100.00,
                    precision_digits=precision), 0)
                self.assertNotEqual(move_line_complete.tax_id_secondary, False)
                continue

    def test_iva_16_currency_supplier(self):
        """Tests Supplier with currency USD and tax 16% with two payments
        """
        cr, uid = self.cr, self.uid
        precision = self.precision_obj.precision_get(cr, uid, 'Account')
        invoice_id = self.create_invoice_supplier(
            cr, uid, 116, [self.tax_16],
            time.strftime('%Y') + '-06-01', self.currency_usd_id)

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
            self.bank_journal_usd_id, time.strftime('%Y') + '-06-01')
        for move_line in move_line_ids_complete:
            if move_line.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(float_compare(
                    move_line.amount_base, 40.30,
                    precision_digits=precision), 0)
                self.assertNotEqual(move_line.tax_id_secondary, False)
                continue

        # create payment complete

        move_line_ids_complete = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, -56,
            self.bank_journal_usd_id, time.strftime('%Y') + '-06-30')
        checked_line = 0
        for move_line_complete in move_line_ids_complete:
            if move_line_complete.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(float_compare(
                    float(move_line_complete.amount_base), 31.58,
                    precision_digits=precision), 0)
                self.assertNotEqual(move_line_complete.tax_id_secondary, False)
                checked_line += 1
                continue
        self.assertEquals(checked_line, 1)

    def test_iva_16_currency_supplier_almost_complete(self):
        """Tests Supplier with currency USD and tax 16% and two payments
            First payment almost complete and exchange rate
                greater then invoice
            Second payment with exchange rate same that invoice
        """
        cr, uid = self.cr, self.uid
        precision = self.precision_obj.precision_get(cr, uid, 'Account')
        invoice_id = self.create_invoice_supplier(
            cr, uid, 116, [self.tax_16],
            time.strftime('%Y') + '-06-30', self.currency_usd_id)

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
            self.bank_journal_usd_id, time.strftime('%Y') + '-06-01')
        for move_line in move_line_ids_complete:
            if move_line.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(float_compare(
                    move_line.amount_base, 77.25,
                    precision_digits=precision), 0)
                self.assertNotEqual(move_line.tax_id_secondary, False)
                continue

        # create payment complete

        move_line_ids_complete = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, -1,
            self.bank_journal_usd_id, time.strftime('%Y') + '-06-30')

        checked_line = 0
        for move_line_complete in move_line_ids_complete:
            if move_line_complete.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(float_compare(
                    move_line_complete.amount_base, 0.56,
                    precision_digits=precision), 0)
                self.assertNotEqual(move_line_complete.tax_id_secondary, False)
                checked_line += 1
                continue
        self.assertEquals(checked_line, 1)

    def test_iva_0_supplier(self):
        """Tests Supplier with tax 0%
        """
        cr, uid = self.cr, self.uid
        invoice_id = self.create_invoice_supplier(
            cr, uid, 100, [self.tax_0], time.strftime('%Y') + '-07-01')

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
        move_line_ids = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, -100,
            self.bank_journal_id)

        self.assertEquals(len(move_line_ids), 4)
        for move_line in move_line_ids:
            if move_line.account_id.id == self.acc_tax_0_payment:
                self.assertEquals(move_line.amount_base, 100.0)
                self.assertNotEqual(move_line.tax_id_secondary, False)
                continue

    def test_iva_0_supplier_usd(self):
        """Tests Supplier with tax 0% with USD
        """
        cr, uid = self.cr, self.uid
        invoice_id = self.create_invoice_supplier(
            cr, uid, 100, [self.tax_0], time.strftime('%Y') + '-07-01',
            self.currency_usd_id)

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
        move_line_ids = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, -100,
            self.bank_journal_usd_id)

        self.assertEquals(len(move_line_ids), 4)
        for move_line in move_line_ids:
            if move_line.account_id.id == self.acc_tax_0_payment:
                self.assertEquals(move_line.amount_base, 65.41)
                self.assertNotEqual(move_line.tax_id_secondary, False)
                continue
