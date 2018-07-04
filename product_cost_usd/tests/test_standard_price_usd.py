# coding: utf-8

from __future__ import division

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.tools import float_round, float_compare
from odoo import fields


class TestStandardPriceUsd(TransactionCase):

    def setUp(self):
        super(TestStandardPriceUsd, self).setUp()
        self.mxn = self.env.ref('base.MXN')
        self.usd = self.env.ref('base.USD')
        self.sale_order = self.env['sale.order']
        self.partner = self.env.ref('base.res_partner_4')
        self.product_uom = self.env.ref('product.product_uom_unit')
        self.product = self.env.ref('product.product_product_24')
        self.pricelist_15_usd = self.env['product.pricelist'].create({
            'name': 'Pricelist 15% USD',
            'currency_id': self.usd.id,
            'item_ids': [(0, 0, {
                    'compute_price': 'formula',
                    'base': 'standard_price_usd',  # based on cost in usd
                    'price_discount': -15,
                })]
        })
        self.pricelist_15_mxn = self.pricelist_15_usd.copy({
            'name': 'Pricelist 15% MXN',
            'currency_id': self.mxn.id})
        self.pricelist = self.env['product.pricelist'].create({
            'name': 'Pricelist Demo'})

    def set_standard_price_usd(self, price):
        self.assertTrue(self.product.seller_ids)
        self.product.seller_ids[0].write({
            'currency_id': self.usd.id,
            'price': price})

    def test_01(self):
        """ Test USD pricelist based on cost in usd. """
        self.set_standard_price_usd(880)
        product = self.product.with_context(pricelist=self.pricelist_15_usd.id)
        expected_price = float_round(
            product.standard_price_usd * 1.15,
            precision_rounding=self.usd.rounding)
        self.assertEqual(
            float_compare(product.price, expected_price, precision_digits=2),
            0, "Product price should be %s" % product.price)

    def test_02(self):
        """ Test a MXN pricelist based on cost in usd. """
        self.set_standard_price_usd(880)
        product = self.product.with_context(pricelist=self.pricelist_15_mxn.id)
        mxn_rate = (self.mxn.rate / self.usd.rate)
        expected_price = float_round(
            (product.standard_price_usd * 1.15) * mxn_rate,
            precision_rounding=self.mxn.rounding)
        self.assertEqual(
            float_compare(product.price, expected_price, precision_digits=2),
            0, "Product price should be %s" % product.price)

    def test_sale_margin(self):
        """ Test the sale margin module using a pricelist with cost in usd. """
        self.set_standard_price_usd(880)
        product = self.product.with_context(pricelist=self.pricelist_15_mxn.id)
        # Create a sale order for product Graphics Card.
        sale_order = self.sale_order.create({
            'date_order': fields.Datetime.now(),
            'name': 'Test',
            'order_line': [(0, 0, {
                'name': '[CARD] Graphics Card',
                'product_uom': self.product_uom.id,
                'product_uom_qty': 1,
                'state': 'draft',
                'product_id': product.id})],
            'partner_id': self.partner.id,
            'pricelist_id': self.pricelist_15_mxn.id})
        # Confirm the sale order.
        sale_order.action_confirm()
        # Verify that margin field gets bind with the value.
        mxn_rate = (self.mxn.rate / self.usd.rate)
        expected_price = float_round(
            (product.standard_price_usd * 1.15) * mxn_rate,
            precision_rounding=self.mxn.rounding)
        expected_cost = float_round(
            product.standard_price_usd * mxn_rate,
            precision_rounding=self.mxn.rounding)
        margin = float_round(
            expected_price - expected_cost,
            precision_rounding=self.mxn.rounding)
        self.assertEqual(
            float_compare(sale_order.margin, margin, precision_digits=2),
            0, "Sale order margin should be %s" % margin)

    def test_sale_margin_normal(self):
        """ Test the sale margin module using a pricelist without cost in
        usd.
        """
        # Create a sale order for product Graphics Card.
        sale_order = self.sale_order.create({
            'date_order': fields.Datetime.now(),
            'name': 'Test',
            'order_line': [(0, 0, {
                'name': '[CARD] Graphics Card',
                'product_uom': self.product_uom.id,
                'product_uom_qty': 1,
                'state': 'draft',
                'product_id': self.product.id})],
            'partner_id': self.partner.id,
            'pricelist_id': self.pricelist.id})
        # Confirm the sale order.
        sale_order.action_confirm()
        # Verify that margin field gets bind with the value.
        msg = "Sale order margin should be 9.0"
        self.assertEqual(sale_order.margin, 9.0, msg)
