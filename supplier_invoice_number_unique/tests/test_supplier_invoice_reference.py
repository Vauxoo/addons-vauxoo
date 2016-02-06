# coding: utf-8
# ##########################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    Coded by: Luis Torres (luis_t@vauxoo.com)
# ##########################################################################
from openerp.tests.common import TransactionCase
from openerp import workflow
from openerp import exceptions


class TestReferenceSupplierInvoiceUnique(TransactionCase):

    def setUp(self):
        super(TestReferenceSupplierInvoiceUnique, self).setUp()
        self.invoice = self.env['account.invoice']
        self.inv_demo = self.env.ref('account.test_invoice_1')
        self.partner_demo1 = self.env.ref('base.res_partner_1')
        self.partner_demo2 = self.env.ref('base.res_partner_17')
        self.partner_demo_contact = self.env.ref('base.res_partner_address_2')

    def test_10_validate_invoice_with_reference_unique(self):
        'Test to validate a invoice with reference unique'
        invoice = self.inv_demo.copy()
        invoice.write({'supplier_invoice_number': 'Test10'})
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice.id, 'invoice_open', self.cr)
        self.assertEquals(
            invoice.state, 'open', 'This invoice has not state in open')

    def test_11_validate_invoice_with_ref_unique_uper_lowercase(self):
        'Test to validate a invoice with reference unique, but a reference '\
            'in uppercase'
        invoice = self.inv_demo.copy()
        invoice2 = self.inv_demo.copy()
        invoice.write({'supplier_invoice_number': 'Test10'})
        invoice2.write({'supplier_invoice_number': 'TEST10'})
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice.id, 'invoice_open', self.cr)
        self.assertEquals(
            invoice.state, 'open', 'This invoice has not state in open')
        with self.assertRaisesRegexp(
                exceptions.Warning,
                'Error you can not validate the invoice with '
                'supplier invoice number duplicated.'):
            workflow.trg_validate(
                self.uid, 'account.invoice', invoice2.id, 'invoice_open',
                self.cr)

    def test_12_validate_invoice_with_ref_unique_hyphen(self):
        'Test to validate a invoice with reference unique, but a reference '\
            'with hyphen'
        invoice = self.inv_demo.copy()
        invoice2 = self.inv_demo.copy()
        invoice.write({'supplier_invoice_number': 'Test10'})
        invoice2.write({'supplier_invoice_number': 'Test-10'})
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice.id, 'invoice_open', self.cr)
        self.assertEquals(
            invoice.state, 'open', 'This invoice has not state in open')
        with self.assertRaisesRegexp(
                exceptions.Warning,
                'Error you can not validate the invoice with '
                'supplier invoice number duplicated.'):
            workflow.trg_validate(
                self.uid, 'account.invoice', invoice2.id, 'invoice_open',
                self.cr)

    def test_13_validate_invoice_with_ref_unique_space(self):
        'Test to validate a invoice with reference unique, but a reference '\
            'with a space.'
        invoice = self.inv_demo.copy()
        invoice2 = self.inv_demo.copy()
        invoice.write({'supplier_invoice_number': 'Test10'})
        invoice2.write({'supplier_invoice_number': 'Test 10'})
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice.id, 'invoice_open', self.cr)
        self.assertEquals(
            invoice.state, 'open', 'This invoice has not state in open')
        with self.assertRaisesRegexp(
                exceptions.Warning,
                'Error you can not validate the invoice with '
                'supplier invoice number duplicated.'):
            workflow.trg_validate(
                self.uid, 'account.invoice', invoice2.id, 'invoice_open',
                self.cr)

    def test_20_validate_invoice_without_reference(self):
        'Test to validate a invoice without reference'
        invoice = self.inv_demo.copy()
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice.id, 'invoice_open', self.cr)
        self.assertEquals(
            invoice.state, 'open', 'This invoice has not state in open')

    def test_21_validate_2_invoice_without_reference(self):
        'Test to validate 2 invoices without reference'
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

    def test_30_validate_invoice_with_reference_duplicate_in_draft(self):
        'Test to validate a invoice with reference duplicated, but with '\
            'this is duplicated in a invoice in draft, I validate an '\
            ' invoice and after try validate the second invoice'
        invoice = self.inv_demo.copy()
        invoice2 = self.inv_demo.copy()
        invoice.write({'supplier_invoice_number': 'Test10'})
        invoice2.write({'supplier_invoice_number': 'Test10'})
        workflow.trg_validate(
            self.uid, 'account.invoice', invoice.id, 'invoice_open', self.cr)
        self.assertEquals(
            invoice.state, 'open', 'This invoice has not state in open')
        with self.assertRaisesRegexp(
                exceptions.Warning,
                'Error you can not validate the invoice with '
                'supplier invoice number duplicated.'):
            workflow.trg_validate(
                self.uid, 'account.invoice', invoice2.id, 'invoice_open',
                self.cr)

    def test_40_validate_invoice_with_reference_duplicated_in_cancel(self):
        'Test to validate a invoice with reference duplicated, but a invoice'\
            ' state is cancel'
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
        'Test to validate 2 invoices with the reference, but to different'\
            'supplier'
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

    def test_51_validate_2_invoice_with_same_ref_supplier_contact(self):
        'Test to validate 2 invoices with same reference, but a supplier '\
            'is a contact'
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
        self.cr.commit()
        with self.assertRaisesRegexp(
                exceptions.Warning,
                'Error you can not validate the invoice with '
                'supplier invoice number duplicated.'):
            workflow.trg_validate(
                self.uid, 'account.invoice', invoice2.id, 'invoice_open',
                self.cr)
