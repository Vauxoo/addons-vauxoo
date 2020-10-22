from odoo.tests.common import TransactionCase


class TestStockLogisticsWarehouse(TransactionCase):

    def setUp(self):
        super(TestStockLogisticsWarehouse, self).setUp()
        self.picking_obj = self.env['stock.picking']
        self.product_obj = self.env['product.product'].with_context(tracking_disable=True)
        self.template_obj = self.env['product.template']
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')
        self.stock_location = self.env.ref(
            'stock.stock_location_stock')
        self.customer_location = self.env.ref('stock.stock_location_customers')
        self.uom_unit = self.env.ref('uom.product_uom_unit')

        # Create attribute
        self.attribute = self.env['product.attribute'].create({'name': 'Type',
                                                               'sequence': 1})
        self.attribute_a = self.env['product.attribute.value'].create({
            'name': 'A',
            'attribute_id': self.attribute.id,
            'sequence': 1,
        })
        self.attribute_b = self.env['product.attribute.value'].create({
            'name': 'B',
            'attribute_id': self.attribute.id,
            'sequence': 2,
        })

        # Create product template
        self.template_ab = self.template_obj.create(
            {'name': 'templAB',
             'standard_price': 1,
             'type': 'product',
             'uom_id': self.uom_unit.id,
             'attribute_line_ids': [(0, 0, {
                 'attribute_id': self.attribute.id,
                 'value_ids': [(6, 0, (self.attribute_a + self.attribute_b).ids)]
             })],
             })
        self.product_values = {'name': 'product A',
                               'default_code': 'A',
                               }

    def update_product(self, position, values):
        self.template_ab.product_variant_ids[position].write(values)
        return self.template_ab.product_variant_ids[position]

    def create_picking(self, picking_type, loc_orig, loc_dest, product, qty):
        picking = self.picking_obj.create({
            'picking_type_id': picking_type,
            'location_id': loc_orig.id,
            'location_dest_id': loc_dest.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': product.id,
                    'product_uom': product.uom_id.id,
                    'product_uom_qty': qty,
                    'location_id': loc_orig.id,
                    'location_dest_id': loc_dest.id,
                })]
        })
        return picking

    def compare_qty_available_not_res(self, product, value):
        product.refresh()
        self.assertEqual(product.qty_available_not_res, value)

    def test01_stock_levels(self):
        """checking that qty_available_not_res actually reflects \
        the variations in stock, both on product and template"""

        # Update product A and B

        product_a = self.update_product(0, self.product_values)
        self.product_values.update({'name': 'product B',
                                    'default_code': 'B',
                                    })
        product_b = self.update_product(1, self.product_values)

        # Create a picking move from INCOMING to STOCK

        picking_in_a = self.create_picking(self.ref('stock.picking_type_in'),
                                           self.supplier_location,
                                           self.stock_location,
                                           product_a, 2)

        picking_in_b = self.create_picking(self.ref('stock.picking_type_in'),
                                           self.supplier_location,
                                           self.stock_location,
                                           product_b, 3)

        self.compare_qty_available_not_res(product_a, 0)
        self.compare_qty_available_not_res(self.template_ab, 0)

        picking_in_a.action_confirm()
        self.compare_qty_available_not_res(product_a, 0)
        self.compare_qty_available_not_res(self.template_ab, 0)

        picking_in_a.action_assign()
        self.compare_qty_available_not_res(product_a, 0)
        self.compare_qty_available_not_res(self.template_ab, 0)

        picking_in_a.move_line_ids.write({'qty_done': 2})
        picking_in_a.button_validate()
        self.compare_qty_available_not_res(product_a, 2)
        self.compare_qty_available_not_res(self.template_ab, 2)

        picking_in_b.action_confirm()
        picking_in_b.action_assign()
        picking_in_b.move_line_ids.write({'qty_done': 3})
        picking_in_b.button_validate()
        self.compare_qty_available_not_res(product_a, 2)
        self.compare_qty_available_not_res(product_b, 3)

        self.compare_qty_available_not_res(self.template_ab, 5)

        # Create a picking from STOCK to CUSTOMER
        picking_out_a = self.create_picking(self.ref('stock.picking_type_out'),
                                            self.stock_location,
                                            self.customer_location,
                                            product_b, 2)

        self.compare_qty_available_not_res(product_b, 3)
        self.compare_qty_available_not_res(self.template_ab, 5)

        picking_out_a.action_confirm()
        self.compare_qty_available_not_res(product_b, 3)
        self.compare_qty_available_not_res(self.template_ab, 5)

        picking_out_a.action_assign()
        self.compare_qty_available_not_res(product_b, 1)
        self.compare_qty_available_not_res(self.template_ab, 3)

        picking_out_a.move_line_ids.write({'qty_done': 2})
        picking_out_a.button_validate()
        self.compare_qty_available_not_res(product_b, 1)
        self.compare_qty_available_not_res(self.template_ab, 3)
