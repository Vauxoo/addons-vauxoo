import json

from odoo import Command
from odoo.tests import TransactionCase, tagged


@tagged("sale_order", "post_install", "-at_install")
class TestStockByWarehouseSale(TransactionCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Storable Test Product",
                "is_storable": True,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(cls.product, cls.warehouse.lot_stock_id, 10.0)

    def test_01_sale_order_line_warehouse_stock(self) -> None:
        """Verify that warehouses_stock is correctly computed on demand in sale order lines."""
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 5.0,
                        }
                    ),
                ],
            }
        )

        # By default, warehouses_stock_recompute is False, so warehouses_stock should be False
        sale_order_line = sale_order.order_line
        self.assertFalse(sale_order_line.warehouses_stock)

        # Invalidate product cache to force a fresh DB read of the stock levels
        self.product.invalidate_recordset()

        # Assert product quantity to populate cache and verify initial stock level
        self.assertEqual(self.product.qty_available_not_res, 10.0)

        # Enable warehouses_stock_recompute to trigger the warehouse stock computation
        sale_order_line.write({"warehouses_stock_recompute": True})

        # The field should automatically compute on read when warehouses_stock_recompute changes
        stock_info = json.loads(sale_order_line.warehouses_stock)

        self.assertTrue(stock_info)
        self.assertEqual(stock_info.get("warehouse"), 10.0)
