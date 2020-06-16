from odoo import tools
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.modules.module import get_resource_path


class TestInvoiceLineAssetCategory(TransactionCase):

    def _load(self, module, *args):
        tools.convert_file(
            self.cr, 'account_asset', get_resource_path(module, *args),
            {}, 'init', False, 'test', self.registry._assertion_report)

    def create_invoice(self, journal, a_pay, uom, inv_type='out_invoice', product=None,
                       price=100.0):
        invoice = self.invoice_model.create({
            'partner_id': self.partner.id,
            'company_id': self.company,
            'type': inv_type,
            'journal_id': journal,
            'account_id': a_pay.id,
        })
        self.create_invoice_line(invoice, product, uom, price)
        return invoice

    def create_invoice_line(self, invoice, a_pay, product, uom, price, quantity=1):
        if product is None:
            product = self.product
        line = self.invoice_line_obj.new({
            'product_id': product.id,
            'invoice_id': invoice.id,
            'uom_id': uom.id,
            'quantity': quantity,
            'price_unit': price,
            'account_id': a_pay.id,
        })
        line._onchange_product_id()
        values = line._convert_to_write(line._cache)
        return self.invoice_line_obj.create(values)

    def setUp(self):
        super(TestInvoiceLineAssetCategory, self).setUp()
        self.invoice_obj = self.env['account.invoice']
        self.invoice_line_obj = self.env['account.invoice.line']
        self.company = self.env.ref('base.main_company')
        self.partner = self.env.ref('base.res_partner_3')
        self.sales_journal = self.env.ref(
            'account_invoice_line_asset_category_required.sales_journal')
        self.a_pay = self.env.ref('account_invoice_line_asset_category_required.a_pay')
        self.a_sale = self.env.ref('account_invoice_line_asset_category_required.a_sale')
        self.product = self.env.ref('product.product_product_4')
        self.uom = self.env.ref('uom.product_uom_hour')

        self.invoice = self.create_invoice(
            self.sales_journal, self.a_pay, self.uom,
            inv_type='in_invoice', product=self.product, price=5355.0)

        self._load('account', 'test', 'account_minimal_test.xml')
        self._load('account_asset', 'test', 'account_asset_demo_test.xml')
        self.category_asset = self.env.ref(
            'account_asset.account_asset_category_fixedassets_test0')

    def test_01_line_with_police_always_set(self):
        """Create an invoice with a line that need category, ideal case"""
        invoice = self.invoice.copy()
        for line in invoice.invoice_line_ids:
            line.account_id.user_type.write({'asset_policy': 'always'})
            line.write({'asset_category_id': self.category_asset.id})
        invoice.signal_workflow('invoice_open')

    def test_02_line_with_police_never_not_set(self):
        """Create an invoice with a line that not need category, ideal case"""
        invoice = self.invoice.copy()
        for line in invoice.invoice_line_ids:
            line.account_id.user_type.write({'asset_policy': 'never'})
        invoice.signal_workflow('invoice_open')

    def test_03_line_with_police_always_not_set(self):
        """Create an invoice with a line that need category, but this not is set"""
        invoice = self.invoice.copy()
        for line in invoice.invoice_line_ids:
            line.account_id.user_type.write({'asset_policy': 'always'})
        with self.assertRaisesRegexp(
                ValidationError, "Asset policy is set to 'Always'"):
            invoice.signal_workflow('invoice_open')

    def test_04_line_with_police_never_set(self):
        """Create an invoice with a line that not need category, but this is set"""
        invoice = self.invoice.copy()
        for line in invoice.invoice_line_ids:
            line.account_id.user_type.write({'asset_policy': 'never'})
            line.write({'asset_category_id': self.category_asset.id})
        with self.assertRaisesRegexp(
                ValidationError, "Asset policy is set to 'Never'"):
            invoice.signal_workflow('invoice_open')
