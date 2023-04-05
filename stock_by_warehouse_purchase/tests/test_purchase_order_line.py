from odoo.tests import Form, TransactionCase, tagged
from odoo.tools.safe_eval import safe_eval


@tagged("purchase_order_line")
class TestStockLogisticsWarehousePurchase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env.ref("base.res_partner_3")
        cls.product1 = cls.env.ref("product.product_product_5")
        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.env.user.groups_id |= cls.env.ref("stock.group_stock_multi_warehouses")

    def create_purchase_order(self, partner=None, **line_kwargs):
        if partner is None:
            partner = self.customer
        order = Form(self.env["purchase.order"])
        order.partner_id = partner
        order = order.save()
        self.create_purchase_order_line(order, **line_kwargs)
        return order

    def create_purchase_order_line(self, order, product=None, quantity=1, price=150):
        if product is None:
            product = self.product1
        with Form(order) as form_ord, form_ord.order_line.new() as line:
            line.product_id = product
            line.price_unit = price
            line.product_qty = quantity

    def test_01_part_number_default_for_report(self):
        # Create a purchase order
        purchase_order = self.create_purchase_order()
        # Now, there are no stock for this product
        self.assertFalse(purchase_order.order_line.warehouses_stock)
        with Form(purchase_order) as purchase, purchase.order_line.edit(0) as line:
            line.warehouses_stock_recompute = True
            self.assertEqual(safe_eval(line.warehouses_stock)["warehouse"], 0)
        # Update the stock for this product
        self.env["stock.quant"]._update_available_quantity(self.product1, self.location, 10)
        # Now, there are products
        self.assertFalse(purchase_order.order_line.warehouses_stock)
        with Form(purchase_order) as purchase, purchase.order_line.edit(0) as line:
            line.warehouses_stock_recompute = True
            self.assertEqual(safe_eval(line.warehouses_stock)["warehouse"], 10)
