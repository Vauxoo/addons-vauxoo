# coding: utf-8
# ##########################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    Coded by: Luis Torres (luis_t@vauxoo.com)
# ##########################################################################

from openerp import workflow
from openerp import exceptions
from openerp.tests.common import TransactionCase
from openerp.tools import mute_logger


class TestReferenceSupplierInvoiceUnique(TransactionCase):

    def setUp(self):
        super(TestReferenceSupplierInvoiceUnique, self).setUp()
        self.invoice = self.env['account.invoice']
        self.inv_demo = self.env.ref('account.test_invoice_1')
        self.partner_demo1 = self.env.ref('base.res_partner_1')
        self.partner_demo2 = self.env.ref('base.res_partner_17')
        self.partner_demo_contact = self.env.ref('base.res_partner_address_2')

    def test_10_validate_invoice_with_reference_unique(self):
        """Validate an invoice with reference unique"""
        invoice = self.inv_demo.copy()
        invoice.write({'supplier_invoice_number': 'Test10'})
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice.id, 'invoice_open', self.cr)
        self.assertEquals(
            invoice.state, 'open', 'This invoice has not state in open')

    @mute_logger('openerp.sql_db')
    def test_11_validate_invoice_with_ref_unique_uper_lowercase(self):
        """Validate an invoice with reference unique, but a reference in
        uppercase"""
        invoice = self.inv_demo.copy()
        invoice2 = self.inv_demo.copy()
        invoice.write({'supplier_invoice_number': 'Test10'})
        invoice2.write({'supplier_invoice_number': 'TEST10'})
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice.id, 'invoice_open', self.cr)
        self.assertEquals(
            invoice.state, 'open', 'This invoice has not state in open')
        with self.assertRaisesRegexp(
                exceptions.Warning, 'Error you can not validate the invoice '
                'with supplier invoice number duplicated.'):
            invoice2.signal_workflow('invoice_open')

    @mute_logger('openerp.sql_db')
    def test_12_validate_invoice_with_ref_unique_hyphen(self):
        """Validate an invoice with reference unique, but a reference with
        hyphen"""
        invoice = self.inv_demo.copy()
        invoice2 = self.inv_demo.copy()
        invoice.write({'supplier_invoice_number': 'Test10'})
        invoice2.write({'supplier_invoice_number': 'Test-10'})
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice.id, 'invoice_open', self.cr)
        self.assertEquals(
            invoice.state, 'open', 'This invoice has not state in open')
        with self.assertRaisesRegexp(
                exceptions.Warning, 'Error you can not validate the invoice '
                'with supplier invoice number duplicated.'):
            invoice2.signal_workflow('invoice_open')

    @mute_logger('openerp.sql_db')
    def test_13_validate_invoice_with_ref_unique_space(self):
        """Validate an invoice with reference unique, but a reference with a
        space."""
        invoice = self.inv_demo.copy()
        invoice2 = self.inv_demo.copy()
        invoice.write({'supplier_invoice_number': 'Test10'})
        invoice2.write({'supplier_invoice_number': 'Test 10'})
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice.id, 'invoice_open', self.cr)
        self.assertEquals(
            invoice.state, 'open', 'This invoice has not state in open')
        with self.assertRaisesRegexp(
                exceptions.Warning, 'Error you can not validate the invoice '
                'with supplier invoice number duplicated.'):
            invoice2.signal_workflow('invoice_open')

    def test_20_validate_invoice_without_reference(self):
        """Validate an invoice without reference"""
        invoice = self.inv_demo.copy()
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice.id, 'invoice_open', self.cr)
        self.assertEquals(
            invoice.state, 'open', 'This invoice has not state in open')

    def test_21_validate_2_invoice_without_reference(self):
        """Validate 2 invoices without reference"""
        invoice = self.inv_demo.copy()
        invoice2 = self.inv_demo.copy()
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice.id, 'invoice_open', self.cr)
        self.assertEquals(
            invoice.state, 'open', 'This invoice has not state in open')
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice2.id, 'invoice_open', self.cr)
        self.assertEquals(
            invoice2.state, 'open', 'This invoice has not state in open')

    @mute_logger('openerp.sql_db')
    def test_30_validate_invoice_with_reference_duplicate_in_draft(self):
        """Validate an invoice with reference duplicated, but the duplicated
        invoice is in draft.Is validated an invoice and after try validate
        the second"""
        invoice = self.inv_demo.copy()
        invoice2 = self.inv_demo.copy()
        invoice.write({'supplier_invoice_number': 'Test10'})
        invoice2.write({'supplier_invoice_number': 'Test10'})
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice.id, 'invoice_open', self.cr)
        self.assertEquals(
            invoice.state, 'open', 'This invoice has not state in open')
        with self.assertRaisesRegexp(
                exceptions.Warning, 'Error you can not validate the invoice '
                'with supplier invoice number duplicated.'):
            invoice2.signal_workflow('invoice_open')

    def test_40_validate_invoice_with_reference_duplicated_in_cancel(self):
        """Validate a invoice with reference duplicated, but and invoice
        cancelled"""
        invoice = self.inv_demo.copy()
        invoice2 = self.inv_demo.copy()
        invoice.write({'supplier_invoice_number': 'Test10'})
        invoice2.write({'supplier_invoice_number': 'Test10'})
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice2.id, 'invoice_cancel',
            self.cr)
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice.id, 'invoice_open', self.cr)

    def test_50_validate_2_invoice_with_same_reference_diff_supplier(self):
        """Validate 2 invoices with the same reference, but to different
        supplier"""
        invoice = self.inv_demo.copy()
        invoice2 = self.inv_demo.copy()
        invoice.write({
            'supplier_invoice_number': 'Test50',
            'partner_id': self.partner_demo1.id
        })
        invoice2.write({
            'supplier_invoice_number': 'Test50',
            'partner_id': self.partner_demo2.id
        })
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice.id, 'invoice_open', self.cr)
        self.assertEquals(
            invoice.state, 'open', 'This invoice has not state in open')
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice2.id, 'invoice_open', self.cr)
        self.assertEquals(
            invoice2.state, 'open', 'This invoice2 has not state in open')

    @mute_logger('openerp.sql_db')
    def test_51_validate_2_invoice_with_same_ref_supplier_contact(self):
        """Validate 2 invoices with the same reference, but a supplier is a
        contact"""
        invoice = self.inv_demo.copy()
        invoice2 = self.inv_demo.copy()
        invoice.write({
            'supplier_invoice_number': 'Test50',
            'partner_id': self.partner_demo1.id
        })
        invoice2.write({
            'supplier_invoice_number': 'Test50',
            'partner_id': self.partner_demo_contact.id
        })
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice.id, 'invoice_open', self.cr)
        self.assertEquals(
            invoice.state, 'open', 'This invoice has not state in open')
        with self.assertRaisesRegexp(
                exceptions.Warning, 'Error you can not validate the invoice '
                'with supplier invoice number duplicated.'):
            invoice2.signal_workflow('invoice_open')
