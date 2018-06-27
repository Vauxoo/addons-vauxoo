# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2016 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Luis Torres <luis_t@vauxoo.com>
############################################################################
from openerp.tests.common import TransactionCase
from openerp.exceptions import ValidationError


class TestInvoiceLineAssetCategory(TransactionCase):

    def setUp(self):
        super(TestInvoiceLineAssetCategory, self).setUp()
        self.invoice_obj = self.env['account.invoice']
        self.invoice_line_obj = self.env['account.invoice.line']

        self.invoice = self.env.ref(
            'account_invoice_line_asset_category_required.'
            'invoice_demo_asset_category')
        self.category_asset = self.env.ref(
            'account_asset.account_asset_category_fixedassets0')

    def test_01_line_with_police_always_set(self):
        "Create an invoice with a line that need category, ideal case"
        invoice = self.invoice.copy()
        for line in invoice.invoice_line_ids:
            line.account_id.user_type.write({'asset_policy': 'always'})
            line.write({'asset_category_id': self.category_asset.id})
        invoice.signal_workflow('invoice_open')

    def test_02_line_with_police_never_not_set(self):
        "Create an invoice with a line that not need category, ideal case"
        invoice = self.invoice.copy()
        for line in invoice.invoice_line_ids:
            line.account_id.user_type.write({'asset_policy': 'never'})
        invoice.signal_workflow('invoice_open')

    def test_03_line_with_police_always_not_set(self):
        "Create an invoice with a line that need category, but this not is set"
        invoice = self.invoice.copy()
        for line in invoice.invoice_line_ids:
            line.account_id.user_type.write({'asset_policy': 'always'})
        with self.assertRaisesRegexp(
                ValidationError, "Asset policy is set to 'Always'"):
            invoice.signal_workflow('invoice_open')

    def test_04_line_with_police_never_set(self):
        "Create an invoice with a line that not need category, but this is set"
        invoice = self.invoice.copy()
        for line in invoice.invoice_line_ids:
            line.account_id.user_type.write({'asset_policy': 'never'})
            line.write({'asset_category_id': self.category_asset.id})
        with self.assertRaisesRegexp(
                ValidationError, "Asset policy is set to 'Never'"):
            invoice.signal_workflow('invoice_open')
