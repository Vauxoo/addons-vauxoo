from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import Form, TransactionCase, tagged
from odoo.tools import float_compare


@tagged("post_install", "-at_install", "sale")
class TestStandardPriceUsd(TransactionCase):
    def setUp(self):
        super().setUp()
        self.mxn = self.env.ref("base.MXN")
        self.usd = self.env.ref("base.USD")
        self.partner = self.env.ref("base.res_partner_4")
        self.product_uom = self.env.ref("uom.product_uom_unit")
        self.product = self.env.ref("product.product_product_24")
        self.pricelist_15_usd = self.env.ref("product_cost_usd.pricelist_15_usd")
        self.pricelist_15_mxn = self.pricelist_15_usd.copy({"name": "Pricelist 15% MXN", "currency_id": self.mxn.id})
        self.pricelist = self.env["product.pricelist"].create({"name": "Pricelist Demo"})

    def create_sale_order(self, product=None, partner=None, pricelist=None, **line_kwargs):
        if partner is None:
            partner = self.partner
        order = Form(self.env["sale.order"])
        order.date_order = fields.Datetime.now()
        order.partner_id = partner
        order.pricelist_id = pricelist
        with order.order_line.new() as line:
            line.product_id = product
            line.product_uom = self.product_uom
            line.product_uom_qty = 1
        order = order.save()
        return order

    def set_standard_price_usd(self, price):
        self.assertTrue(self.product.seller_ids)
        self.product.seller_ids[0].write({"currency_id": self.usd.id})
        self.product.write({"standard_price_usd": price})

    def test_01_usd_pricelist(self):
        """Test USD pricelist based on cost in USD."""
        self.set_standard_price_usd(880)
        product = self.product.with_context(pricelist=self.pricelist_15_usd.id)
        expected_price = self.usd.round(product.standard_price_usd * 1.15)
        self.assertEqual(
            float_compare(product.price, expected_price, precision_digits=2),
            0,
            "Product price should be %s" % product.price,
        )

    def test_02_mxn_pricelist(self):
        """Test a MXN pricelist based on cost in USD."""
        self.set_standard_price_usd(880)
        product = self.product.with_context(pricelist=self.pricelist_15_mxn.id)
        mxn_rate = self.mxn.rate / self.usd.rate
        expected_price = self.mxn.round((product.standard_price_usd * 1.15) * mxn_rate)
        self.assertEqual(
            float_compare(product.price, expected_price, precision_digits=2),
            0,
            "Product price should be %s" % product.price,
        )

    def test_03_constraint_check_cost_no_seller(self):
        """Test constraint check_cost_and_price."""
        self.product.seller_ids = False
        with self.assertRaisesRegex(ValidationError, "You must have at least one supplier with price in USD"):
            self.product.write({"standard_price_usd": 880})

    def test_04_constraint_check_cost(self):
        """Test constraint check_cost_and_price."""
        with self.assertRaisesRegex(ValidationError, "You cannot create or modify a product if the cost in USD"):
            self.set_standard_price_usd(1)

    def test_05_sale_margin(self):
        """Test the sale margin module using a pricelist with cost in USD."""
        self.set_standard_price_usd(880)
        # Create a sale order for product Graphics Card.
        sale_order = self.create_sale_order(product=self.product, pricelist=self.pricelist_15_mxn)
        # Confirm the sale order.
        sale_order.action_confirm()
        # Verify that margin field gets bind with the value.
        mxn_rate = self.mxn.rate / self.usd.rate
        expected_price = self.mxn.round((self.product.standard_price_usd * 1.15) * mxn_rate)
        expected_cost = self.mxn.round(self.product.standard_price_usd * mxn_rate)
        margin = self.mxn.round(expected_price - expected_cost)
        self.assertEqual(
            float_compare(sale_order.margin, margin, precision_digits=2), 0, "Sale order margin should be %s" % margin
        )

    def test_06_sale_margin_normal(self):
        """Test the sale margin module using a pricelist without cost in
        USD.
        """
        # Create a sale order for product Graphics Card.
        sale_order = self.create_sale_order(product=self.product, pricelist=self.pricelist)
        # Confirm the sale order.
        sale_order.action_confirm()
        # Verify that margin field gets bind with the value.
        msg = "Sale order margin should be 9.0"
        self.assertEqual(sale_order.margin, 9.0, msg)
