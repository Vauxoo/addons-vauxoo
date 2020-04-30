from odoo.tests.common import TransactionCase


class TestStockLogisticsWarehouse(TransactionCase):

    def setUp(self):
        super(TestStockLogisticsWarehouse, self).setUp()
        self.picking_obj = self.env['stock.picking']
        self.product_obj = self.env['product.product']
        self.template_obj = self.env['product.template']
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')
        self.stock_location = self.env.ref(
            'stock.stock_location_stock')
        self.customer_location = self.env.ref('stock.stock_location_customers')
        self.uom_unit = self.env.ref('uom.product_uom_unit')

        # Create product template
        self.template_ab = self.template_obj.create(
            {'name': 'templAB',
             'uom_id': self.uom_unit.id,
             })

        self.product_values = {'name': 'product A',
                               'standard_price': 1,
                               'type': 'product',
                               'uom_id': self.uom_unit.id,
                               'default_code': 'A',
                               'product_tmpl_id': self.template_ab.id,
                               }

    def create_product(self, values):
        return self.product_obj.create(values)

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

    def test01_stock_levels(self):
        """checking that qty_available_not_res actually reflects \
        the variations in stock, both on product and template"""

        # Create product A and B

        product_a = self.create_product(self.product_values)
        product_b = product_a.copy({'name': 'product B',
                                    'default_code': 'B',
                                    'product_tmpl_id': self.template_ab.id})

        # Create a picking move from INCOMING to STOCK

        picking_in_a = self.create_picking(self.ref('stock.picking_type_in'),
                                           self.supplier_location,
                                           self.stock_location,
                                           product_a, 2)

        picking_in_b = self.create_picking(self.ref('stock.picking_type_in'),
                                           self.supplier_location,
                                           self.stock_location,
                                           product_b, 3)

        def compare_qty_available_not_res(product, value):
            # Refresh, because the function field is not recalculated between
            # transactions
            product.refresh()
            self.assertEqual(product.qty_available_not_res, value)

        compare_qty_available_not_res(product_a, 0)
        compare_qty_available_not_res(self.template_ab, 0)

        picking_in_a.action_confirm()
        compare_qty_available_not_res(product_a, 0)
        compare_qty_available_not_res(self.template_ab, 0)

        picking_in_a.action_assign()
        compare_qty_available_not_res(product_a, 0)
        compare_qty_available_not_res(self.template_ab, 0)

        picking_in_a.move_line_ids.write({'qty_done': 2})
        picking_in_a.do_transfer()
        compare_qty_available_not_res(product_a, 2)
        compare_qty_available_not_res(self.template_ab, 2)

        # will directly trigger action_done on productB
        picking_in_b.move_line_ids.write({'qty_done': 3})
        picking_in_b.do_transfer()
        compare_qty_available_not_res(product_a, 2)
        compare_qty_available_not_res(product_b, 3)

        compare_qty_available_not_res(self.template_ab, 5)

        # Create a picking from STOCK to CUSTOMER
        picking_out_a = self.create_picking(self.ref('stock.picking_type_out'),
                                            self.stock_location,
                                            self.customer_location,
                                            product_b, 2)

        compare_qty_available_not_res(product_b, 3)
        compare_qty_available_not_res(self.template_ab, 5)

        picking_out_a.action_confirm()
        compare_qty_available_not_res(product_b, 3)
        compare_qty_available_not_res(self.template_ab, 5)

        picking_out_a.action_assign()
        compare_qty_available_not_res(product_b, 1)
        compare_qty_available_not_res(self.template_ab, 3)

        picking_out_a.move_line_ids.write({'qty_done': 2})
        picking_out_a.do_transfer()
        compare_qty_available_not_res(product_b, 1)
        compare_qty_available_not_res(self.template_ab, 3)
