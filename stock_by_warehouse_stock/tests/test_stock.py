# Copyright 2020 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json
from odoo.tests import TransactionCase, Form, tagged


@tagged('stock')
class TestStock(TransactionCase):
    def setUp(self):
        super(TestStock, self).setUp()
        self.customer = self.env.ref('base.res_partner_2')
        self.product = self.env.ref('product.product_product_6')
        self.product_available = self.env.ref('product.product_product_27')  # FURN_8855
        self.product_unavailable = self.env.ref('product.product_product_3')  # FURN_7800
        self.picking_type_out = self.env.ref('stock.picking_type_out')  # WH-DELIVERY
        self.picking_type_in = self.env.ref('stock.picking_type_in')  # WH-RECEIPTS

    def create_stock_picking(self, customer, stock_picking_type):
        """Method to create a new picking, it receives a customer and a stock_picking_type. With this type
        of creation the methods onchange will be raise."""
        picking_form = Form(self.env['stock.picking'])
        picking_form.partner_id = customer
        picking_form.picking_type_id = stock_picking_type
        return picking_form.save()

    def create_new_stock_picking_line_form(self, stock_picking, product_id, qty=5):
        """Method to create a new picking line, it receives a picking, a product and it can or not receive a
        quantity for the product. With this type of creation the methods onchange will be raise."""
        with Form(stock_picking) as picking:
            with picking.move_ids_without_package.new() as line:
                line.product_id = product_id
                line.product_uom_qty = qty

    def test_01_set_location_move_line(self):
        """Testing that the location that is being suggested from the widget 'product_available_stock_move'
        (field 'warehouses_stock') are automatically applied in the stock move lines 'location_id' field."""

        stock_picking = self.create_stock_picking(self.customer, self.picking_type_out)
        self.create_new_stock_picking_line_form(stock_picking, self.product_available, qty=20)
        self.create_new_stock_picking_line_form(stock_picking, self.product_unavailable, qty=20)

        stock_picking.action_confirm()

        stock_move_available = stock_picking.move_lines[0]
        stock_move_unavailable = stock_picking.move_lines[1]

        with Form(stock_move_available, 'stock.view_stock_move_operations') as stock_move:
            stock_move.warehouses_stock_recompute = True
            with stock_move.move_line_ids.new() as line:
                line.qty_done = 20

        warehouse_stock_locations_available_str = self.product_available.with_context(
            warehouse=stock_move_available.warehouse_id)._compute_get_stock_location()
        warehouse_stock_locations_available = json.loads(warehouse_stock_locations_available_str)['content']
        best_location_available = warehouse_stock_locations_available[0]['most_quantity_location_id']

        # The location_id on the stock move line should have the best_location_available.
        stock_move_available_line = stock_move_available.move_line_ids[0]
        self.assertEqual(stock_move_available_line.location_id.id, best_location_available)
        self.assertEqual(stock_move_available_line.location_id, stock_move_available.suggested_location_id)

        with Form(stock_move_unavailable, 'stock.view_stock_move_operations') as stock_move:
            stock_move.warehouses_stock_recompute = True
            with stock_move.move_line_ids.new() as line:
                line.qty_done = 20

        warehouse_stock_locations_unavailable_str = self.product_unavailable.with_context(
            warehouse=stock_move_unavailable.warehouse_id)._compute_get_stock_location()
        warehouse_stock_locations_unavailable = json.loads(warehouse_stock_locations_unavailable_str)['content']
        best_location_unavailable = bool(warehouse_stock_locations_unavailable)

        # This stock move line should not have the best_location_available.
        self.assertFalse(best_location_unavailable)
        self.assertFalse(stock_move_unavailable.suggested_location_id)
        self.assertEqual(stock_move_unavailable.move_line_ids[0].location_id, stock_move_unavailable.location_id)

    def test_02_check_locations_available(self):
        """Testing new product with 2 locations available, after creating a new location, this location doesn't need
        to be in the location that are being placed as available."""

        # Creating a new product, with no availability, but with the field 'tracking' as "lot"
        product = self.env.ref('stock_by_warehouse_stock.demo_product_new')
        # Getting the Stock and Stock/Shelf 1 locations
        stock_location = self.env.ref('stock.stock_location_stock')
        stock_shelf_location = self.env.ref('stock.stock_location_components')

        # Creating the new location with the stock location as parent.
        new_loc = self.env['stock.location'].create({
            'name': 'Position', 'location_id': stock_location.id, 'usage': 'internal'
            })

        # Creating 2 new lots of the product
        stock_lot_1 = self.env['stock.production.lot'].create({
            'name': 'Product Test Lot 1', 'product_id': product.id
            })
        stock_lot_2 = self.env['stock.production.lot'].create({
            'name': 'Product Test Lot 2', 'product_id': product.id
            })

        # Creating an adjustment for the product.
        stock_adjustment = self.env['stock.inventory'].create({
            'name': 'Stock Adj.Test Product', 'filter': 'product', 'product_id': product.id
            })
        stock_adjustment.action_start()
        # The adjustment will have the following quantities:
        # Adjustment to Stock of 21 pieces. stock_lot_1: 3 pieces, stock_lot_2: 18 pieces
        # Adjustment to Stock/Shelf of 25 pieces. stock_lot_1: 10 pieces, stocl_lot_2: 15 pieces
        self.env['stock.inventory.line'].create([
            {
                'inventory_id': stock_adjustment.id,
                'location_id': stock_location.id,
                'product_id': product.id,
                'prod_lot_id': stock_lot_1.id,
                'product_qty': 3,
            }, {
                'inventory_id': stock_adjustment.id,
                'location_id': stock_location.id,
                'product_id': product.id,
                'prod_lot_id': stock_lot_2.id,
                'product_qty': 18,
            }, {
                'inventory_id': stock_adjustment.id,
                'location_id': stock_shelf_location.id,
                'product_id': product.id,
                'prod_lot_id': stock_lot_1.id,
                'product_qty': 10,
            }, {
                'inventory_id': stock_adjustment.id,
                'location_id': stock_shelf_location.id,
                'product_id': product.id,
                'prod_lot_id': stock_lot_2.id,
                'product_qty': 15,
            }
        ])
        stock_adjustment.action_validate()

        # Creating a Stock picking with the product that will allow us to check if:
        # The Suggested Location for the stock move lines is Stock/Shelf.
        # There are two locations available for the stock move.
        stock_picking = self.create_stock_picking(self.customer,  self.picking_type_out)
        self.create_new_stock_picking_line_form(stock_picking, product, qty=10)
        stock_picking.action_confirm()

        stock_move = stock_picking.move_lines[0]

        with Form(stock_move, 'stock.view_stock_move_operations') as operation:
            operation.warehouses_stock_recompute = True
            with operation.move_line_ids.new() as line:
                line.qty_done = 20

        warehouse_stock_info_str = product.with_context(
            warehouse=stock_move.warehouse_id)._compute_get_stock_location()
        warehouse_stock_info = json.loads(warehouse_stock_info_str)['content']
        best_location_available = warehouse_stock_info[0]['most_quantity_location_id']

        # The location_id on the stock move line should have the best_location_available.
        # The best_location_available should be "Stock/Shelf."
        stock_move_line = stock_move.move_line_ids[0]
        self.assertEqual(stock_move.suggested_location_id.id, best_location_available)
        self.assertEqual(stock_move_line.location_id.id, best_location_available)

        # For the stock move should only be two locations available.
        self.assertEqual(warehouse_stock_info[0]['locations_available'], 2.0)
        # And the new location created at the begging can not be on the locations available.
        locations = [info.get('location') for info in warehouse_stock_info[0]['info_content']]
        self.assertNotIn(new_loc.display_name, locations)
