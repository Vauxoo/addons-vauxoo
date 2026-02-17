from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import Form, TransactionCase, tagged
from odoo.tools import float_compare


@tagged("post_install", "-at_install", "sale")
class TestStandardPriceUsd(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mxn = cls.env.ref("base.MXN")
        cls.usd = cls.env.ref("base.USD")
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.env.user.write({"group_ids": [Command.link(cls.env.ref("product.group_product_pricelist").id)]})
        # Get or create the unit UOM
        cls.product_uom = cls.env.ref("uom.product_uom_unit")
        if not cls.product_uom:
            cls.product_uom = cls.env["uom.uom"].create(
                {
                    "name": "Unit",
                }
            )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "uom_id": cls.product_uom.id,
                "type": "consu",
                "standard_price": 876.0,
                "list_price": 885.0,
            }
        )

        # Create supplier for product
        cls.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "partner_id": cls.partner.id,
                "price": 876.0,
                "currency_id": cls.usd.id,
            }
        )

        # Create pricelist with USD base cost strategy
        cls.pricelist_15_usd = cls.env["product.pricelist"].create(
            {
                "name": "Pricelist 15% USD",
                "currency_id": cls.usd.id,
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "1_product",
                            "product_id": cls.product.id,
                            "base": "standard_price_usd",
                            "compute_price": "formula",
                            "price_discount": -15,
                        }
                    )
                ],
            }
        )
        cls.pricelist_15_mxn = cls.pricelist_15_usd.copy({"name": "Pricelist 15% MXN", "currency_id": cls.mxn.id})
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Pricelist Demo"})

    def create_sale_order(self, product=None, partner=None, pricelist=None, **line_kwargs):
        if partner is None:
            partner = self.partner

        order = Form(self.env["sale.order"])
        order.partner_id = partner
        if pricelist:
            order.pricelist_id = pricelist
        with order.order_line.new() as line:
            line.product_id = product
            line.product_uom_qty = 1
        return order.save()

    def set_standard_price_usd(self, price):
        self.assertTrue(self.product.seller_ids)
        self.product.seller_ids[0].write({"currency_id": self.usd.id})
        self.product.write({"standard_price_usd": price})

    def test_01_usd_pricelist(self):
        """Test USD pricelist based on cost in USD."""
        self.set_standard_price_usd(880)
        product = self.product.with_context(pricelist=self.pricelist_15_usd.id)
        expected_price = self.usd.round(product.standard_price_usd * 1.15)
        product_price = product.get_contextual_price()
        self.assertEqual(
            float_compare(product_price, expected_price, precision_digits=2),
            0,
            "Product price should be %s" % product_price,
        )

    def test_02_mxn_pricelist(self):
        """Test a MXN pricelist based on cost in USD."""
        self.set_standard_price_usd(880)
        product = self.product.with_context(pricelist=self.pricelist_15_mxn.id)
        mxn_rate = self.mxn.rate / self.usd.rate
        expected_price = self.mxn.round((product.standard_price_usd * 1.15) * mxn_rate)
        product_price = product.get_contextual_price()
        self.assertEqual(
            float_compare(product_price, expected_price, precision_digits=2),
            0,
            "Product price should be %s" % product_price,
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
