# -*- coding: utf-8 -*-

import time
from odoo.tests.common import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class TestSaleOrder(TransactionCase):
    """Test cases for sale.order model"""

    def setUp(self):
        super(TestSaleOrder, self).setUp()
        self.date_now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        self.partner_camp = self.env.ref('base.res_partner_12')
        self.prod_ipadmini = self.env.ref('product.product_product_6')
        self.demo_user = self.env.ref('base.user_demo')
        self.sale_order_id = self.env['sale.order'].create({
            'partner_id': self.partner_camp.id,
            'order_line': [(0, 0, {
                'name': 'iPadMini',
                'product_id': self.prod_ipadmini.id,
                'product_uom': self.prod_ipadmini.uom_id.id,
                'product_uom_qty': 1,
            })],
        })
        self.sale_order_id.user_id = self.demo_user.id

    def test_01_margin_cost_0(self):
        """ Margin and Margin Percentage when cost is 0.0
        """
        sale = self.sale_order_id
        product = self.prod_ipadmini
        # Need to set the product cost to 0.0 to do not let the margin take
        # into account the real product data instead.
        product.standard_price = 0.0
        sale.write({"order_line": [(6, 0, [])]})
        sale.write({"order_line": [(0, 0, {
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': 4,
            'purchase_price': 0.0,
            'price_unit': 12.0,
        })]})
        self.assertEqual(sale.order_line.margin, 48)
        self.assertEqual(sale.order_line.margin_percentage, 100.0)

    def test_02_margin_sale_price_0(self):
        """ Margin and Margin Percentage when sale price is 0.0
        """
        sale = self.sale_order_id
        sale.write({"order_line": [(6, 0, [])]})
        sale.write({"order_line": [(0, 0, {
            'product_id': self.prod_ipadmini.id,
            'product_uom': self.prod_ipadmini.uom_id.id,
            'product_uom_qty': 4,
            'purchase_price': 15.0,
            'price_unit': 0.0,
        })]})
        self.assertEqual(sale.order_line.margin, -60)
        self.assertEqual(sale.order_line.margin_percentage, -100)

    def test_03_margin_sale_qty_0(self):
        """ Margin and Margin Percentage when product qty is 0.0
        """
        sale = self.sale_order_id
        sale.write({"order_line": [(6, 0, [])]})
        sale.write({"order_line": [(0, 0, {
            'product_id': self.prod_ipadmini.id,
            'product_uom': self.prod_ipadmini.uom_id.id,
            'product_uom_qty': 0,
            'purchase_price': 10.0,
            'price_unit': 15.0,
        })]})
        self.assertEqual(sale.order_line.margin, 0.0)
        self.assertEqual(sale.order_line.margin_percentage, 0.0)

    def test_04_margin_positive(self):
        """ Margin and Margin Percentage when purchase price < sale cost
        """
        sale = self.sale_order_id
        sale.write({"order_line": [(6, 0, [])]})
        sale.write({"order_line": [(0, 0, {
            'product_id': self.prod_ipadmini.id,
            'product_uom': self.prod_ipadmini.uom_id.id,
            'product_uom_qty': 4,
            'purchase_price': 10.0,
            'price_unit': 12.0,
        })]})
        self.assertEqual(sale.order_line.margin, 8.0)
        self.assertAlmostEqual(sale.order_line.margin_percentage, 16.66,
                               places=1)

    def test_05_margin_negative(self):
        """ Margin and Margin Percentage when purchase price > sale cost
        """
        sale = self.sale_order_id
        sale.write({"order_line": [(6, 0, [])]})
        sale.write({"order_line": [(0, 0, {
            'product_id': self.prod_ipadmini.id,
            'product_uom': self.prod_ipadmini.uom_id.id,
            'product_uom_qty': 4,
            'purchase_price': 15.0,
            'price_unit': 12.0,
        })]})
        self.assertEqual(sale.order_line.margin, -12)
        self.assertAlmostEqual(sale.order_line.margin_percentage, -25,
                               places=1)

    def test_06_margin_balanced(self):
        """ Margin and Margin Percentage when purchase price = sale cost
        """
        sale = self.sale_order_id
        sale.write({"order_line": [(6, 0, [])]})
        sale.write({"order_line": [(0, 0, {
            'product_id': self.prod_ipadmini.id,
            'product_uom': self.prod_ipadmini.uom_id.id,
            'product_uom_qty': 4,
            'purchase_price': 15.0,
            'price_unit': 15.0,
        })]})
        self.assertEqual(sale.order_line.margin, 0.0)
        self.assertEqual(sale.order_line.margin_percentage, 0.0)

    def test_07_margin_total(self):
        """ Margin Percentage of the sale order.
        """
        # Need to set the product cost to 0.0 to do not let the margin take
        # into account the real product data instead.
        product = self.prod_ipadmini
        product.standard_price = 0.0

        lines = [
            {'product_uom_qty': 4, 'price_unit': 12.0, 'purchase_price': 0.0},
            {'product_uom_qty': 4, 'price_unit': 0.0, 'purchase_price': 15.0},
            {'product_uom_qty': 4, 'price_unit': 12.0, 'purchase_price': 15.0},
            {'product_uom_qty': 4, 'price_unit': 12.0, 'purchase_price': 10.0},
            {'product_uom_qty': 4, 'price_unit': 12.0, 'purchase_price': 12.0},
            {'product_uom_qty': 0, 'price_unit': 15.0, 'purchase_price': 10.0},
            {'product_uom_qty': 4, 'price_unit': 13.0, 'purchase_price': 5.0},
            {'product_uom_qty': 5, 'price_unit': 12.0, 'purchase_price': 10.0},
        ]
        for line in lines:
            line.update(product_id=product.id, product_uom=product.uom_id.id)

        sale = self.sale_order_id
        sale.write({"order_line": [(6, 0, [])]})
        sale.write({"order_line": [(0, 0, line) for line in lines]})

        self.assertEqual(sale.order_line.mapped("margin"),
                         [48.0, -60.0, -12.0, 8.0, 0.0, 0.0, 32.0, 10.0])
        self.assertEqual(sale.order_line.mapped("margin_percentage"),
                         [100.0, -100.0, -25.0, 16.67, 0.0, 0.0, 61.54, 16.67])
        self.assertEqual(sale.margin, 26)
        self.assertAlmostEqual(sale.margin_percentage, 8.55, places=1)
