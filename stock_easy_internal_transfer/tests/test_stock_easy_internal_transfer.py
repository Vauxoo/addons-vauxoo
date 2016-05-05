# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Jose Suniaga (josemiguel@vauxoo.com)
#    Planified by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Audited by: Jose Morales <jose@vauxoo.com>
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.tests.common import TransactionCase
from openerp import exceptions


class TestStockEasyInternalTransfer(TransactionCase):

    def setUp(self):
        super(TestStockEasyInternalTransfer, self).setUp()
        self.prod = self.env.ref('product.product_product_38')
        self.stock = self.env.ref('stock.stock_location_stock')
        self.shelf1 = self.env.ref('stock.stock_location_components')
        self.shelf2 = self.env.ref('stock.stock_location_14')
        self.wh = self.env.ref('stock.warehouse0')
        self.wh.write({'use_easy_internal': True})
        self.easy_domain = [
            ('warehouse_id', '=', self.wh.id),
            ('code', '=', 'internal'),
            ('quick_view', '=', True),
            ('name', '=', 'Quick Internal Transfers')
        ]

    def create_inventory(self):
        inventory = self.env['stock.inventory'].create({
            'name': 'Ink invetory test',
            'location_id': self.stock.id,
            'filter': 'partial',
            'line_ids': [(0, 0, {
                'product_id': self.prod.id,
                'product_uom_id': self.prod.uom_id.id,
                'location_id': self.stock.id,
                'product_qty': 2000,
            })]
        })
        inventory.prepare_inventory()
        inventory.action_done()
        return inventory

    def create_picking(self):
        """Utility to create pickings during the test.
        """
        picking_type = self.env['stock.picking.type'].search(self.easy_domain)
        values = {
            'origin': 'Easy Internal Picking Test',
            'picking_type_id': picking_type.id,
            'force_location_id': self.stock.id,
        }
        picking = self.env['stock.picking'].create(values)
        self.assertTrue(picking)
        return picking

    def test_01_warehouse_has_quick_internal_transfer(self):
        picking_type = self.env['stock.picking.type'].search(self.easy_domain)
        self.assertTrue(picking_type,
                        "Warehouse %s should have a type of Operation"
                        "'Quick Internal Transfer'" % self.wh.name)

    def test_02_quick_internal_transfer_done(self):
        self.create_inventory()
        picking = self.create_picking()
        picking.write({'move_lines': [(0, 0, {
            'name': 'Ink test',
            'product_id': self.prod.id,
            'product_uom_qty': 2000.0,
            'product_uom': self.prod.uom_id.id,
            'location_id': self.stock.id,
            'location_dest_id': self.shelf1.id,
        })]})

        # Change next state and check it
        picking.action_confirm()
        self.assertEqual(picking.state, 'confirmed',
                         "Signal 'confirm' don't work fine!")
        # Change next state and check it
        picking.action_assign()
        self.assertEqual(picking.state, 'assigned',
                         "Signal 'assigned' don't work fine!")
        picking.write({'force_location_dest_id': self.shelf1.id})
        picking.do_detailed_transfer()
        self.assertEqual(picking.state, 'done',
                         "Signal 'done' don't work fine!")

    def test_03_quick_internal_transfer_qty_not_available(self):
        self.create_inventory()
        picking = self.create_picking()
        picking.write({'move_lines': [(0, 0, {
            'name': 'Ink test',
            'product_id': self.prod.id,
            'product_uom_qty': 3000.0,
            'product_uom': self.prod.uom_id.id,
            'location_id': self.stock.id,
            'location_dest_id': self.shelf1.id,
        })]})

        # Change next state and check it
        picking.action_confirm()
        self.assertEqual(picking.state, 'confirmed',
                         "Signal 'confirm' don't work fine!")

        # Error raised expected with message expected.
        with self.assertRaises(exceptions.Warning):
            picking.action_assign()

    def test_04_do_2_quick_internal_transfer_1_done_1_assigned(self):
        self.create_inventory()
        picking_done = self.create_picking()
        picking_done.write({'move_lines': [(0, 0, {
            'name': 'Ink test',
            'product_id': self.prod.id,
            'product_uom_qty': 1680.0,
            'product_uom': self.prod.uom_id.id,
            'location_id': self.stock.id,
            'location_dest_id': self.shelf1.id,
        })]})

        # Change next state and check it
        picking_done.action_confirm()
        self.assertEqual(picking_done.state, 'confirmed',
                         "Signal 'confirm' don't work fine!")
        # Change next state and check it
        picking_done.action_assign()
        self.assertEqual(picking_done.state, 'assigned',
                         "Signal 'assigned' don't work fine!")
        picking_done.write({'force_location_dest_id': self.shelf1.id})
        picking_done.do_detailed_transfer()
        self.assertEqual(picking_done.state, 'done',
                         "Signal 'done' don't work fine!")
        picking_assigned = self.create_picking()
        picking_assigned.write({'move_lines': [(0, 0, {
            'name': 'Ink test',
            'product_id': self.prod.id,
            'product_uom_qty': 400.0,
            'product_uom': self.prod.uom_id.id,
            'location_id': self.stock.id,
            'location_dest_id': self.shelf2.id,
        })]})

        # Change next state and check it
        picking_assigned.action_confirm()
        self.assertEqual(picking_assigned.state, 'confirmed',
                         "Signal 'confirm' don't work fine!")

        # Error raised expected with message expected.
        with self.assertRaises(exceptions.Warning):
            picking_assigned.action_assign()

    def test_05_do_2_quick_internal_transfer_2_done_and_check_quant(self):
        self.create_inventory()
        picking_done_1 = self.create_picking()
        picking_done_1.write({'move_lines': [(0, 0, {
            'name': 'Ink test',
            'product_id': self.prod.id,
            'product_uom_qty': 1600.0,
            'product_uom': self.prod.uom_id.id,
            'location_id': self.stock.id,
            'location_dest_id': self.shelf1.id,
        })]})

        # Change next state and check it
        picking_done_1.action_confirm()
        self.assertEqual(picking_done_1.state, 'confirmed',
                         "Signal 'confirm' don't work fine!")
        # Change next state and check it
        picking_done_1.action_assign()
        self.assertEqual(picking_done_1.state, 'assigned',
                         "Signal 'assigned' don't work fine!")
        picking_done_1.write({'force_location_dest_id': self.shelf1.id})
        picking_done_1.do_detailed_transfer()
        self.assertEqual(picking_done_1.state, 'done',
                         "Signal 'done' don't work fine!")
        picking_done_2 = self.create_picking()
        picking_done_2.write({'move_lines': [(0, 0, {
            'name': 'Ink test',
            'product_id': self.prod.id,
            'product_uom_qty': 300.0,
            'product_uom': self.prod.uom_id.id,
            'location_id': self.stock.id,
            'location_dest_id': self.shelf2.id,
        })]})

        # Change next state and check it
        picking_done_2.action_confirm()
        self.assertEqual(picking_done_2.state, 'confirmed',
                         "Signal 'confirm' don't work fine!")
        # Change next state and check it
        picking_done_2.action_assign()
        self.assertEqual(picking_done_2.state, 'assigned',
                         "Signal 'assigned' don't work fine!")
        picking_done_2.write({'force_location_dest_id': self.shelf2.id})
        picking_done_2.do_detailed_transfer()
        self.assertEqual(picking_done_2.state, 'done',
                         "Signal 'done' don't work fine!")
        domain_quants = [
            ('product_id', '=', self.prod.id),
            ('location_id', '=', self.stock.id),
            ('reservation_id', '=', False)
        ]
        quants = self.env['stock.quant'].search(domain_quants)
        total_qty = quants and sum(quants.mapped('qty')) or 0.0
        self.assertEqual(total_qty, 100.0,
                         "Should have exactly 100.0 of %s in location"
                         " %s" % (self.prod.name, self.stock.name))
