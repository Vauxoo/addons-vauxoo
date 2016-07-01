# coding: utf-8
from openerp.addons.account_voucher_tax.tests.common import TestTaxCommon
from openerp.exceptions import Warning as UserError
import time


class TestPaymentTax(TestTaxCommon):
    """These Tests were made based on this document,
        https://docs.google.com/a/vauxoo.com/spreadsheets/d/1O82bBb-mySbpH7SiY1KQILsIIRMgcO5E0ddNuCGC0N8/edit#gid=0
        to test the successful creation of taxes efectivamete pagado / cobrado
        of supplier in payments by bank statement
    """

    def setUp(self):
        super(TestPaymentTax, self).setUp()

    def test_iva_16_supplier(self):
        """Tests Supplier with tax 16% and two payments
        """
        cr, uid = self.cr, self.uid
        invoice_id = self.account_invoice_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.invoice_supplier_journal_id,
            'reference_type': 'none',
            'name': 'invoice to supplier',
            'account_id': self.account_payable_id,
            'type': 'in_invoice',
            'date_invoice': time.strftime('%Y') + '-07-01',
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
                continue

    def test_iva_16_ret_supplier(self):
        """Tests Supplier with two taxes IVA 16%
            and Retention 10.67% with one payment
        """
        cr, uid = self.cr, self.uid
        invoice_id = self.account_invoice_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.invoice_supplier_journal_id,
            'reference_type': 'none',
            'name': 'invoice to supplier',
            'account_id': self.account_payable_id,
            'type': 'in_invoice',
            'date_invoice': time.strftime('%Y') + '-07-01',
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

        amount_iva16 = 0.0
        checked_line = 0
        for move_line_complete in move_line_ids_complete:
            if move_line_complete.account_id.id == self.acc_tax16:
                amount_iva16 += move_line_complete.credit
                self.assertEquals(move_line_complete.debit, 0.0)
                if move_line_complete.credit == 10.67:
                    checked_line += 1
                if move_line_complete.credit == 5.33:
                    checked_line += 1
                self.assertEquals(move_line_complete.amount_residual, 0.0)
                self.assertTrue(move_line_complete.reconcile_id,
                                "Reconcile should be created.")
                continue
            if move_line_complete.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(move_line_complete.debit, 5.33)
                self.assertEquals(move_line_complete.credit, 0.0)
                checked_line += 1
                continue

            # retention tax validation
            if move_line_complete.account_id.id == self.acc_ret1067:
                self.assertEquals(move_line_complete.debit, 10.67)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(move_line_complete.amount_residual, 0.0)
                self.assertTrue(move_line_complete.reconcile_id,
                                "Reconcile should be created.")
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_ret1067_payment:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(move_line_complete.credit, 10.67)
                checked_line += 1
                continue

            # iva pending for apply by retention
            if move_line_complete.account_id.id == self.acc_tax_pending_apply:
                self.assertEquals(move_line_complete.debit, 10.67)
                self.assertEquals(move_line_complete.credit, 0.0)
                checked_line += 1
                continue
        self.assertEquals(checked_line, 6)
        self.assertEquals(amount_iva16, 16)

    def test_iva_16_currency_supplier(self):
        """Tests Supplier with currency USD and tax 16% with two payments
        """
        cr, uid = self.cr, self.uid
        invoice_id = self.account_invoice_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.invoice_supplier_journal_id,
            'reference_type': 'none',
            'name': 'invoice to supplier',
            'account_id': self.account_payable_id,
            'type': 'in_invoice',
            'date_invoice': time.strftime('%Y') + '-06-01',
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
            self.bank_journal_usd_id, time.strftime('%Y') + '-06-01')
        for move_line in move_line_ids_complete:
            if move_line.account_id.id == self.acc_tax16 and\
                    move_line.amount_currency:
                self.assertEquals(move_line.debit, 0.0)
                self.assertEquals(move_line.credit, 6.45)
                self.assertEquals(round(move_line.amount_residual, 2), -6.02)
                self.assertEquals(move_line.amount_currency, -8.28)
                self.assertTrue(move_line.reconcile_partial_id,
                                "Partial Reconcile should be created.")
                continue
            if move_line.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(move_line.debit, 6.45)
                self.assertEquals(move_line.credit, 0.0)
                self.assertEquals(move_line.amount_currency, 8.28)
                continue

        # create payment complete

        move_line_ids_complete = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, -56,
            self.bank_journal_usd_id, time.strftime('%Y') + '-06-30')

        checked_line = 0
        for move_line_complete in move_line_ids_complete:
            if move_line_complete.account_id.id == self.acc_tax16 and\
                    move_line_complete.amount_currency == 0:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(move_line_complete.credit, 0.97)
                self.assertEquals(move_line_complete.amount_residual, 0.0)
                self.assertTrue(move_line_complete.reconcile_id,
                                "Reconcile should be created.")
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_tax16 and\
                    move_line_complete.amount_currency:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(move_line_complete.credit, 5.05)
                self.assertEquals(move_line_complete.amount_residual, 0.0)
                self.assertEquals(move_line_complete.amount_currency, -7.72)
                self.assertTrue(move_line_complete.reconcile_id,
                                "Reconcile should be created.")
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(move_line_complete.debit, 5.05)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(move_line_complete.amount_currency, 7.72)
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_loss_tax:
                self.assertEquals(move_line_complete.debit, 0.97)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(move_line_complete.amount_currency, 0)
                checked_line += 1
                continue
        self.assertEquals(checked_line, 4)

    def test_iva_16_currency_supplier_almost_complete(self):
        """Tests Supplier with currency USD and tax 16% and two payments
            First payment almost complete and exchange rate
                greater then invoice
            Second payment with exchange rate same that invoice
        """
        cr, uid = self.cr, self.uid
        invoice_id = self.account_invoice_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.invoice_supplier_journal_id,
            'reference_type': 'none',
            'name': 'invoice to supplier',
            'account_id': self.account_payable_id,
            'type': 'in_invoice',
            'date_invoice': time.strftime('%Y') + '-06-30',
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
            self.bank_journal_usd_id, time.strftime('%Y') + '-06-01')
        for move_line in move_line_ids_complete:
            if move_line.account_id.id == self.acc_tax16 and\
                    move_line.amount_currency:
                self.assertEquals(move_line.debit, 0.0)
                self.assertEquals(move_line.credit, 12.36)
                self.assertEquals(round(move_line.amount_residual, 2), 1.89)
                self.assertEquals(round(move_line.amount_currency, 2), -15.86)
                self.assertTrue(move_line.reconcile_partial_id,
                                "Partial Reconcile should be created.")
                continue
            if move_line.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(move_line.debit, 12.36)
                self.assertEquals(move_line.credit, 0.0)
                self.assertEquals(round(move_line.amount_currency, 2), 15.86)
                continue

        # create payment complete

        move_line_ids_complete = self.create_statement(
            cr, uid, line_id, self.partner_agrolait_id, -1,
            self.bank_journal_usd_id, time.strftime('%Y') + '-06-30')

        checked_line = 0
        for move_line_complete in move_line_ids_complete:
            if move_line_complete.account_id.id == self.acc_tax16 and\
                    move_line_complete.amount_currency == 0:
                self.assertEquals(move_line_complete.debit, 1.98)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(move_line_complete.amount_residual, 0.0)
                self.assertTrue(move_line_complete.reconcile_id,
                                "Reconcile should be created.")
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_tax16 and\
                    move_line_complete.amount_currency:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(move_line_complete.credit, 0.09)
                self.assertEquals(move_line_complete.amount_residual, 0.0)
                self.assertEquals(move_line_complete.amount_currency, -0.14)
                self.assertTrue(move_line_complete.reconcile_id,
                                "Reconcile should be created.")
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(move_line_complete.debit, 0.09)
                self.assertEquals(move_line_complete.credit, 0.0)
                self.assertEquals(move_line_complete.amount_currency, 0.14)
                checked_line += 1
                continue
            if move_line_complete.account_id.id == self.acc_gain_tax:
                self.assertEquals(move_line_complete.debit, 0.0)
                self.assertEquals(move_line_complete.credit, 1.98)
                self.assertEquals(move_line_complete.amount_currency, 0)
                checked_line += 1
                continue
        self.assertEquals(checked_line, 4)

    def test_iva_16_supplier_difference_currency_usd(self):
        """Tests Supplier with invoice currency USD and tax 16% with
            payment with currency of company EUR
            and specific rate in statement line
        """
        cr, uid = self.cr, self.uid
        invoice_id = self.account_invoice_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.invoice_supplier_journal_id,
            'reference_type': 'none',
            'name': 'invoice to supplier',
            'account_id': self.account_payable_id,
            'type': 'in_invoice',
            'date_invoice': time.strftime('%Y') + '-06-01',
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
            cr, uid, line_id, self.partner_agrolait_id, -100,
            self.bank_journal_id, time.strftime('%Y') + '-06-30',
            currency=self.currency_usd_id, amount_currency=-116)

        checked_line = 0
        for move_line in move_line_ids_complete:
            if move_line.account_id.id == self.acc_tax16 and\
                    move_line.amount_currency == 0:
                self.assertEquals(move_line.debit, 1.32)
                self.assertEquals(move_line.credit, 0.0)
                self.assertEquals(move_line.amount_residual, 0.0)
                self.assertTrue(move_line.reconcile_id,
                                "Reconcile should be created.")
                checked_line += 1
                continue
            if move_line.account_id.id == self.acc_tax16 and\
                    move_line.amount_currency:
                self.assertEquals(move_line.debit, 0.0)
                self.assertEquals(round(move_line.credit, 2), 13.79)
                self.assertEquals(move_line.amount_residual, 0)
                self.assertEquals(move_line.amount_currency, -16.0)
                self.assertTrue(move_line.reconcile_id,
                                "Reconcile should be created.")
                checked_line += 1
                continue
            if move_line.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(round(move_line.debit, 2), 13.79)
                self.assertEquals(move_line.credit, 0.0)
                self.assertEquals(move_line.amount_currency, 16.0)
                checked_line += 1
                continue
            if move_line.account_id.id == self.acc_gain_tax:
                self.assertEquals(move_line.debit, 0.0)
                self.assertEquals(move_line.credit, 1.32)
                self.assertEquals(move_line.amount_currency, 0)
                checked_line += 1
                continue
        self.assertEquals(checked_line, 4)

    def test_iva_16_supplier_difference_currency_eur(self):
        """Tests Supplier with invoice currency company EUR and tax 16% with
            payment with currency USD
            and specific rate in statement line
        """
        cr, uid = self.cr, self.uid
        invoice_id = self.account_invoice_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.invoice_supplier_journal_id,
            'reference_type': 'none',
            'name': 'invoice to supplier',
            'account_id': self.account_payable_id,
            'type': 'in_invoice',
            'date_invoice': time.strftime('%Y') + '-06-01',
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
            cr, uid, line_id, self.partner_agrolait_id, -150,
            self.bank_journal_usd_id, time.strftime('%Y') + '-06-30',
            currency=self.currency_eur_id, amount_currency=-116)

        checked_line = 0
        for move_line in move_line_ids_complete:
            if move_line.account_id.id == self.acc_tax16 and\
                    move_line.amount_currency:
                self.assertEquals(move_line.debit, 0.0)
                self.assertEquals(round(move_line.credit, 2), 16.0)
                self.assertEquals(move_line.amount_residual, 0)
                # TO DO: Also we need to validate amount currency
                # self.assertEquals(move_line.amount_currency, -24.46)
                self.assertTrue(move_line.reconcile_id,
                                "Reconcile should be created.")
                checked_line += 1
                continue
            if move_line.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(round(move_line.debit, 2), 16.0)
                self.assertEquals(move_line.credit, 0.0)
                # TO DO: Also we need to validate amount currency
                # self.assertEquals(move_line.amount_currency, 24.46)
                checked_line += 1
                continue
        self.assertEquals(checked_line, 2)

    def test_validate_rounding_high(self):
        """Tests to validate when amount rounding is too high"""
        cr, uid = self.cr, self.uid
        invoice_id = self.account_invoice_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.invoice_supplier_journal_id,
            'reference_type': 'none',
            'name': 'invoice to supplier',
            'account_id': self.account_payable_id,
            'type': 'in_invoice',
            'date_invoice': time.strftime('%Y') + '-06-01',
            'currency_id': self.currency_usd_id,
            'check_total': 100
        })
        self.account_invoice_line_model.create(cr, uid, {
            'product_id': self.product_id,
            'quantity': 1,
            'price_unit': 100,
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
        bank_stmt_id = self.acc_bank_stmt_model.create(cr, uid, {
            'journal_id': self.bank_journal_usd_id,
            'date': time.strftime('%Y') + '-07-01',
        })

        bank_stmt_line_id = self.acc_bank_stmt_line_model.create(cr, uid, {
            'name': 'payment',
            'statement_id': bank_stmt_id,
            'partner_id': self.partner_agrolait_id,
            'amount': -100,
            'date': time.strftime('%Y') + '-07-01'})

        val = {
            'debit': 1454.45,
            'counterpart_move_line_id': line_id.id,
            'name': line_id.name}

        msg = 'Rounding amount is too high'
        with self.assertRaisesRegexp(UserError, msg):
            self.acc_bank_stmt_line_model.process_reconciliation(
                cr, uid, bank_stmt_line_id, [val])
