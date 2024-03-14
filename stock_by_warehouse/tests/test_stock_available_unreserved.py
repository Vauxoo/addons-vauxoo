from odoo.tests import Form, TransactionCase
from odoo.tools.safe_eval import safe_eval


class TestStockLogisticsWarehouse(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_obj = cls.env["stock.picking"]
        cls.product_obj = cls.env["product.product"].with_context(tracking_disable=True)
        cls.template_obj = cls.env["product.template"]
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

        # Create attribute
        cls.attribute = cls.env["product.attribute"].create({"name": "Type", "sequence": 1})
        cls.attribute_a = cls.env["product.attribute.value"].create(
            {
                "name": "A",
                "attribute_id": cls.attribute.id,
                "sequence": 1,
            }
        )
        cls.attribute_b = cls.env["product.attribute.value"].create(
            {
                "name": "B",
                "attribute_id": cls.attribute.id,
                "sequence": 2,
            }
        )

        # Create product template
        cls.template_ab = cls.template_obj.create(
            {
                "name": "templAB",
                "standard_price": 1,
                "type": "product",
                "uom_id": cls.uom_unit.id,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attribute.id,
                            "value_ids": [(6, 0, (cls.attribute_a + cls.attribute_b).ids)],
                        },
                    )
                ],
            }
        )
        cls.product_values = {
            "name": "product A",
            "default_code": "A",
        }
        cls.env.user.groups_id |= cls.env.ref("stock.group_stock_multi_warehouses")

    def update_product(self, position, values):
        self.template_ab.product_variant_ids[position].write(values)
        return self.template_ab.product_variant_ids[position]

    def create_picking(self, picking_type, loc_orig, loc_dest, product, qty):
        picking = self.picking_obj.create(
            {
                "picking_type_id": picking_type,
                "location_id": loc_orig.id,
                "location_dest_id": loc_dest.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": loc_orig.id,
                            "location_dest_id": loc_dest.id,
                        },
                    )
                ],
            }
        )
        return picking

    def compare_qty_available_not_res(self, product, value):
        product.invalidate_recordset()
        self.assertEqual(product.qty_available_not_res, value)

    def test01_stock_levels(self):
        """checking that qty_available_not_res actually reflects \
        the variations in stock, both on product and template"""

        # Update product A and B

        product_a = self.update_product(0, self.product_values)
        self.product_values.update(
            {
                "name": "product B",
                "default_code": "B",
            }
        )
        product_b = self.update_product(1, self.product_values)

        # Create a picking move from INCOMING to STOCK

        picking_in_a = self.create_picking(
            self.ref("stock.picking_type_in"),
            self.supplier_location,
            self.stock_location,
            product_a,
            2,
        )

        picking_in_b = self.create_picking(
            self.ref("stock.picking_type_in"),
            self.supplier_location,
            self.stock_location,
            product_b,
            3,
        )

        self.compare_qty_available_not_res(product_a, 0)
        self.compare_qty_available_not_res(self.template_ab, 0)

        self.assertFalse(product_a.warehouses_stock)
        with Form(product_a) as product:
            product.warehouses_stock_recompute = True
            self.assertEqual(safe_eval(product.warehouses_stock)["warehouse"], 0)

        self.assertFalse(self.template_ab.warehouses_stock)
        with Form(self.template_ab) as product:
            product.warehouses_stock_recompute = True
            self.assertEqual(safe_eval(product.warehouses_stock)["warehouse"], 0)

        picking_in_a.action_confirm()
        self.compare_qty_available_not_res(product_a, 0)
        self.compare_qty_available_not_res(self.template_ab, 0)

        picking_in_a.action_assign()
        self.compare_qty_available_not_res(product_a, 0)
        self.compare_qty_available_not_res(self.template_ab, 0)

        picking_in_a.move_line_ids.write({"quantity": 2, "picked": True})
        picking_in_a.button_validate()
        self.compare_qty_available_not_res(product_a, 2)
        self.compare_qty_available_not_res(self.template_ab, 2)

        self.assertFalse(product_a.warehouses_stock)
        with Form(product_a) as product:
            product.warehouses_stock_recompute = True
            self.assertEqual(safe_eval(product.warehouses_stock)["warehouse"], 2)

        self.assertFalse(self.template_ab.warehouses_stock)
        with Form(self.template_ab) as product:
            product.warehouses_stock_recompute = True
            self.assertEqual(safe_eval(product.warehouses_stock)["warehouse"], 2)

        picking_in_b.action_confirm()
        picking_in_b.action_assign()
        picking_in_b.move_line_ids.write({"quantity": 3, "picked": True})
        picking_in_b.button_validate()
        self.compare_qty_available_not_res(product_a, 2)
        self.compare_qty_available_not_res(product_b, 3)

        self.compare_qty_available_not_res(self.template_ab, 5)

        # Create a picking from STOCK to CUSTOMER
        picking_out_a = self.create_picking(
            self.ref("stock.picking_type_out"),
            self.stock_location,
            self.customer_location,
            product_b,
            2,
        )

        self.compare_qty_available_not_res(product_b, 3)
        self.compare_qty_available_not_res(self.template_ab, 5)

        self.assertFalse(product_b.warehouses_stock)
        with Form(product_b) as product:
            product.warehouses_stock_recompute = True
            self.assertEqual(safe_eval(product.warehouses_stock)["warehouse"], 3)

        self.assertFalse(self.template_ab.warehouses_stock)
        with Form(self.template_ab) as product:
            product.warehouses_stock_recompute = True
            self.assertEqual(safe_eval(product.warehouses_stock)["warehouse"], 5)

        picking_out_a.action_confirm()
        picking_out_a.action_assign()
        self.compare_qty_available_not_res(product_b, 1)
        self.compare_qty_available_not_res(self.template_ab, 3)

        self.assertFalse(product_b.warehouses_stock)
        with Form(product_b) as product:
            product.warehouses_stock_recompute = True
            self.assertEqual(safe_eval(product.warehouses_stock)["warehouse"], 1)

        self.assertFalse(self.template_ab.warehouses_stock)
        with Form(self.template_ab) as product:
            product.warehouses_stock_recompute = True
            self.assertEqual(safe_eval(product.warehouses_stock)["warehouse"], 3)

        picking_out_a.move_line_ids.write({"quantity": 2, "picked": True})
        picking_out_a.button_validate()
        self.compare_qty_available_not_res(product_b, 1)
        self.compare_qty_available_not_res(self.template_ab, 3)
