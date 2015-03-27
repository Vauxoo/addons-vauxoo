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

        self.assertEquals(len(move_line_ids), 4)
        checked_line = 0

        for move_line in move_line_ids:
            if move_line.account_id.id == self.acc_provision_tax_16_customer:
                self.assertEquals(move_line.debit, 16)
                self.assertEquals(move_line.credit, 0.0)
                self.assertEquals(move_line.amount_residual, 16)
                move_line_tax_rec_id = move_line
                checked_line += 1
                continue
            if move_line.account_id.id == self.acc_tax_16_payment_customer:
                self.assertEquals(move_line.debit, 0.0)
                self.assertEquals(move_line.credit, 16)
                checked_line += 1
                continue
            if move_line.account_id.id == self.account_receivable_id:
                move_line_rec_id = move_line
                checked_line += 1
                continue

        self.assertEquals(checked_line, 3)

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
                continue
            if line_invoice.account_id.id == self.acc_tax16_customer:
                move_line_inv_tax_rec_id = line_invoice

        # create reconciliation with account voucher
        voucher_id = self.account_voucher_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.journal_bank_special,
            'account_id': self.account_bnk_id,
            'date': time.strftime('%Y')+'-06-01',
            'type': 'sale',
            'amount': 0
            })
        self.account_voucher_line_model.create(cr, uid, {
            'voucher_id': voucher_id,
            'type': 'dr',
            'move_line_id': move_line_rec_id.id,
            'partner_id': self.partner_agrolait_id,
            'account_id': self.account_receivable_id,
            'amount': 116
            })
        self.account_voucher_line_model.create(cr, uid, {
            'voucher_id': voucher_id,
            'type': 'cr',
            'move_line_id': move_line_inv_id,
            'partner_id': self.partner_agrolait_id,
            'account_id': self.account_receivable_id,
            'amount': 116
            })

        self.account_voucher_model.proforma_voucher(cr, uid, voucher_id, {})

        self.assertEquals(
            len(self.account_voucher_model.browse(
                cr, uid, voucher_id).move_id.line_id), 5)
        checked_line = 0
        for voucher_line in self.account_voucher_model.browse(
                cr, uid, voucher_id).move_id.line_id:

            if voucher_line.account_id.id ==\
                    self.acc_provision_tax_16_customer:
                self.assertEquals(voucher_line.debit, 0.0)
                self.assertEquals(voucher_line.credit, 16)
                self.assertEquals(voucher_line.amount_residual, 0.0)
                self.assertEquals(
                    voucher_line.reconcile_id.name,
                    move_line_tax_rec_id.reconcile_id.name)
                checked_line += 1
                continue
            if voucher_line.account_id.id == self.acc_tax16_customer:
                self.assertEquals(voucher_line.debit, 16)
                self.assertEquals(voucher_line.credit, 0.0)
                self.assertEquals(voucher_line.amount_residual, 0.0)
                self.assertEquals(
                    voucher_line.reconcile_id.name,
                    move_line_inv_tax_rec_id.reconcile_id.name)
                checked_line += 1
                continue

        self.assertEquals(checked_line, 2)

    def test_cf_iva_16_customer_partial_payment(self):
        cr, uid = self.cr, self.uid

        # create advance
        move_line_ids = self.create_statement(
            cr, uid, None, self.partner_agrolait_id, 145,
            self.bank_journal_id, time.strftime('%Y')+'-06-01',
            self.account_receivable_id)

        self.assertEquals(len(move_line_ids), 4)
        checked_line = 0

        for move_line in move_line_ids:
            if move_line.account_id.id == self.acc_provision_tax_16_customer:
                self.assertEquals(move_line.debit, 20)
                self.assertEquals(move_line.credit, 0.0)
                self.assertEquals(move_line.amount_residual, 20)
                move_line_tax_rec_id = move_line
                checked_line += 1
                continue
            if move_line.account_id.id == self.acc_tax_16_payment_customer:
                self.assertEquals(move_line.debit, 0.0)
                self.assertEquals(move_line.credit, 20)
                checked_line += 1
                continue
            if move_line.account_id.id == self.account_receivable_id:
                move_line_rec_id = move_line
                checked_line += 1
                continue

        self.assertEquals(checked_line, 3)

        # create first invoice
        invoice_first_id = self.account_invoice_model.create(cr, uid, {
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
            'invoice_id': invoice_first_id,
            'name': 'product that cost 100'})

        # validate first invoice
        self.registry('account.invoice').signal_workflow(
            cr, uid, [invoice_first_id], 'invoice_open')
        invoice_record = self.account_invoice_model.browse(
            cr, uid, [invoice_first_id])

        for line_invoice_first in invoice_record.move_id.line_id:
            if line_invoice_first.account_id.id == self.account_receivable_id:
                move_line_inv_first_id = line_invoice_first.id
                continue
            if line_invoice_first.account_id.id == self.acc_tax16_customer:
                move_line_inv_first_tax_rec_id = line_invoice_first

        # create second invoice
        invoice_id_second = self.account_invoice_model.create(cr, uid, {
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
            'invoice_id': invoice_id_second,
            'name': 'product that cost 100'})

        # validate second invoice
        self.registry('account.invoice').signal_workflow(
            cr, uid, [invoice_id_second], 'invoice_open')
        invoice_record = self.account_invoice_model.browse(
            cr, uid, [invoice_id_second])

        for line_invoice_second in invoice_record.move_id.line_id:
            if line_invoice_second.account_id.id == self.account_receivable_id:
                move_line_inv_second_id = line_invoice_second.id
                continue
            if line_invoice_second.account_id.id == self.acc_tax16_customer:
                move_line_inv_second_tax_rec_id = line_invoice_second

        # create reconciliation with account voucher
        voucher_id = self.account_voucher_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.journal_bank_special,
            'account_id': self.account_bnk_id,
            'date': time.strftime('%Y')+'-06-01',
            'type': 'sale',
            'amount': 0
            })
        self.account_voucher_line_model.create(cr, uid, {
            'voucher_id': voucher_id,
            'type': 'dr',
            'move_line_id': move_line_rec_id.id,
            'partner_id': self.partner_agrolait_id,
            'account_id': self.account_receivable_id,
            'amount': 145
            })
        self.account_voucher_line_model.create(cr, uid, {
            'voucher_id': voucher_id,
            'type': 'cr',
            'move_line_id': move_line_inv_first_id,
            'partner_id': self.partner_agrolait_id,
            'account_id': self.account_receivable_id,
            'amount': 116
            })
        self.account_voucher_line_model.create(cr, uid, {
            'voucher_id': voucher_id,
            'type': 'cr',
            'move_line_id': move_line_inv_second_id,
            'partner_id': self.partner_agrolait_id,
            'account_id': self.account_receivable_id,
            'amount': 29
            })

        self.account_voucher_model.proforma_voucher(cr, uid, voucher_id, {})

        self.assertEquals(
            len(self.account_voucher_model.browse(
                cr, uid, voucher_id).move_id.line_id), 7)
        checked_line = 0
        for voucher_line in self.account_voucher_model.browse(
                cr, uid, voucher_id).move_id.line_id:

            if voucher_line.account_id.id ==\
                    self.acc_provision_tax_16_customer:
                self.assertEquals(voucher_line.debit, 0.0)
                self.assertEquals(voucher_line.credit, 20)
                self.assertEquals(voucher_line.amount_residual, 0.0)
                self.assertEquals(
                    voucher_line.reconcile_id.name,
                    move_line_tax_rec_id.reconcile_id.name)
                checked_line += 1
                continue
            if voucher_line.account_id.id == self.acc_tax16_customer:
                if voucher_line.debit == 16:
                    self.assertEquals(
                        voucher_line.reconcile_id.name,
                        move_line_inv_first_tax_rec_id.reconcile_id.name)
                    self.assertEquals(voucher_line.amount_residual, 0.0)
                    checked_line += 1
                    continue
                if voucher_line.debit == 4:
                    self.assertEquals(
                        voucher_line.reconcile_partial_id.id,
                        move_line_inv_second_tax_rec_id.reconcile_partial_id.id
                        )
                    self.assertTrue(voucher_line.reconcile_partial_id,
                                    "Partial Reconcile should be created.")
                    checked_line += 1
                    continue

        self.assertEquals(checked_line, 3)
