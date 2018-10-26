# Copyright 2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.account.tests.account_test_classes import AccountingTestCase


class TestAccountInvoice(AccountingTestCase):

    def setUp(self):
        super(TestAccountInvoice, self).setUp()
        self.invoice_obj = self.env['account.invoice']
        self.partner = self.env.ref('base.res_partner_3')
        self.product1 = self.env.ref('product.product_product_3')
        self.product2 = self.env.ref('product.product_product_5')
        self.split_wizard_obj = self.env['account.invoice.split']

    def create_invoice(self):
        invoice = self.invoice_obj.create({
            'name': 'Test Customer Invoice',
            'partner_id': self.partner.id,
        })
        invoice.invoice_line_ids = [
            (0, 0, {
                'product_id': self.product1.id,
                'name': 'Green Shirt',
                'quantity': 10.0,
                'price_unit': 5.0,
                'account_id': invoice.account_id.id,
            }),
            (0, 0, {
                'product_id': self.product2.id,
                'name': 'Gray Pants',
                'quantity': 5,
                'price_unit': 3.0,
                'account_id': invoice.account_id.id,
            }),
        ]
        return invoice

    def test_01_split_with_new_invoice(self):
        """Test case: split an invoice without creating a new one

        This splits an invoice, without creating a new one to cover the
        remaining amount, and setting the amount to 20%
        """
        invoice = self.create_invoice()
        wizard = self.split_wizard_obj.create({
            'invoice_id': invoice.id,
            'percent': 20.0,
            'create_invoice': False,
        })
        result = wizard.action_split_invoice()

        # Validate fields of the invoice
        self.assertFalse(wizard.new_invoice_id)
        self.assertListEqual(
            invoice.invoice_line_ids.mapped('quantity'), [2.0, 1.0])
        self.assertListEqual(
            invoice.invoice_line_ids.mapped('price_total'), [10.0, 3.0])

        # Validate fields of the returned action
        self.assertTrue(result)
        self.assertEqual(result['view_mode'], 'form')
        self.assertEqual(
            result['domain'], [('id', 'in', invoice.ids)])

    def test_02_split_with_new_invoice(self):
        """Test case: split an invoice creating a new one

        This splits an invoice, creating a new one to cover the remaining
        amount, and setting the amount to 30%.

        First invoice's total amount should be 30% of the original amount, and
        the new one should be 70%.
        """
        invoice = self.create_invoice()
        wizard = self.split_wizard_obj.create({
            'invoice_id': invoice.id,
            'percent': 30.0,
            'create_invoice': True,
        })
        result = wizard.action_split_invoice()

        # Validate fields of the current invoice
        self.assertListEqual(
            invoice.invoice_line_ids.mapped('quantity'), [3.0, 1.5])
        self.assertListEqual(
            invoice.invoice_line_ids.mapped('price_total'), [15.0, 4.5])

        # Validate fields of the created invoice
        new_invoice = wizard.new_invoice_id
        products = self.product1 + self.product2
        self.assertEqual(len(new_invoice.invoice_line_ids), 2)
        self.assertEqual(
            new_invoice.invoice_line_ids.mapped('product_id'), products)
        self.assertListEqual(
            new_invoice.invoice_line_ids.mapped('quantity'), [7.0, 3.5])
        self.assertListEqual(
            new_invoice.invoice_line_ids.mapped('price_total'), [35.0, 10.5])

        # Validate fields of the returned action
        self.assertTrue(result)
        self.assertEqual(result['view_mode'], 'tree,form')
        self.assertEqual(
            result['domain'], [('id', 'in', [invoice.id, new_invoice.id])])
