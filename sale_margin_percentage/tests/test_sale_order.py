from odoo.tests import Form, TransactionCase, tagged


@tagged("sale_order", "post_install", "-at_install")
class TestSaleOrder(TransactionCase):
    """Test cases for sale.order model"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        product = cls.env["product.product"]
        cls.product_cost_0 = product.create({"name": "Product Cost 0", "standard_price": 0.0})
        cls.product_cost_5 = product.create({"name": "Product Cost 5", "standard_price": 5.0})
        cls.product_cost_10 = product.create({"name": "Product Cost 10", "standard_price": 10.0})
        cls.product_cost_12 = product.create({"name": "Product Cost 12", "standard_price": 12.0})
        cls.product_cost_15 = product.create({"name": "Product Cost 15", "standard_price": 15.0})

    def create_so(self, partner=None, **line_kwargs):
        if partner is None:
            partner = self.partner
        order = Form(self.env["sale.order"])
        order.partner_id = partner
        order = order.save()
        self.create_so_line(order, **line_kwargs)
        return order

    def create_so_line(self, order, product=None, quantity=4, price=10):
        if product is None:
            product = self.product_cost_0
        with Form(order) as order_form:
            with order_form.order_line.new() as line:
                line.product_id = product
                line.product_uom_qty = quantity
                line.price_unit = price

    def test_01_margin_cost_0(self):
        """Margin and Margin Percentage when cost is 0"""
        sale = self.create_so(quantity=4, price=12)
        self.assertEqual(sale.order_line.margin, 48)
        self.assertEqual(sale.order_line.margin_percent, 1.0)

    def test_02_margin_sale_price_0(self):
        """Margin and Margin Percentage when sale price is 0"""
        sale = self.create_so(product=self.product_cost_15, quantity=4, price=0)
        self.assertEqual(sale.order_line.margin, -60)
        self.assertEqual(sale.order_line.margin_percent, -1.0)

    def test_03_margin_sale_qty_0(self):
        """Margin and Margin Percentage when product qty is 0"""
        sale = self.create_so(product=self.product_cost_10, quantity=0, price=15)
        self.assertEqual(sale.order_line.margin, 0.0)
        self.assertEqual(sale.order_line.margin_percent, 0.0)

    def test_04_margin_positive(self):
        """Margin and Margin Percentage when purchase price < sale cost"""
        sale = self.create_so(product=self.product_cost_10, quantity=4, price=12)
        self.assertEqual(sale.order_line.margin, 8.0)
        self.assertAlmostEqual(sale.order_line.margin_percent, 0.1666, places=3)

    def test_05_margin_negative(self):
        """Margin and Margin Percentage when purchase price > sale cost"""
        sale = self.create_so(product=self.product_cost_15, quantity=4, price=12)
        self.assertEqual(sale.order_line.margin, -12)
        self.assertAlmostEqual(sale.order_line.margin_percent, -0.25, places=3)

    def test_06_margin_balanced(self):
        """Margin and Margin Percentage when purchase price = sale cost"""
        sale = self.create_so(product=self.product_cost_15, quantity=4, price=15)
        self.assertEqual(sale.order_line.margin, 0.0)
        self.assertEqual(sale.order_line.margin_percent, 0.0)

    def test_07_margin_total(self):
        """Margin Percentage of the sale order."""
        sale = self.create_so(quantity=4, price=12)
        self.create_so_line(sale, product=self.product_cost_15, quantity=4, price=0)
        self.create_so_line(sale, product=self.product_cost_15, quantity=4, price=12)
        self.create_so_line(sale, product=self.product_cost_10, quantity=4, price=12)
        self.create_so_line(sale, product=self.product_cost_12, quantity=4, price=12)
        self.create_so_line(sale, product=self.product_cost_10, quantity=0, price=15)
        self.create_so_line(sale, product=self.product_cost_5, quantity=4, price=13)
        self.create_so_line(sale, product=self.product_cost_10, quantity=5, price=12)
        self.assertEqual(sale.order_line.mapped("margin"), [48.0, -60.0, -12.0, 8.0, 0.0, 0.0, 32.0, 10.0])
        self.assertEqual(
            list(map(lambda x: round(x, 4), sale.order_line.mapped("margin_percent"))),
            [1.0, -1.0, -0.25, 0.1667, 0.0, 0.0, 0.6154, 0.1667],
        )
        self.assertEqual(sale.margin, 26)
        self.assertAlmostEqual(sale.margin_percent, 0.0855, places=3)
