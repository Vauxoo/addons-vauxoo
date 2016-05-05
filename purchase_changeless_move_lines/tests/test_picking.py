# -*- coding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Katherine Zaoral <kathy@vauxoo.com>
#    Audited by: Katherine Zaoral <kathy@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp.addons.purchase_changeless_move_lines.tests.common \
    import TestStockCommon


class TestPicking(TestStockCommon):

    def setUp(self):
        super(TestPicking, self).setUp()

    def test_01_picking(self):
        """Stock Picking CRUD: Create, Read, Update, Duplicate, and Delete
        """
        # Create Picking: Create manually and check it was correctly created
        # in draft state, with no purchase_id releated. and with change_picking
        # = True.
        product = self.product_obj.browse(self.product)
        picking = self.picking_obj.create({
            'partner_id': self.partner,
            'picking_type_id': self.picking_type_in,
            'move_lines': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': 1,
                'product_uom': product.uom_id.id,
                'location_id': self.supp_location,
                'location_dest_id': self.location,
            })]
        })
        self.assertTrue(picking)
        self.assertEqual(picking.state, 'draft')
        self.assertFalse(picking.purchase_id)
        self.assertTrue(picking.change_picking)

        # Update Picking: By default the picking move lines can be modificated
        # (change_picking = True)

        # Modificate the product qty in move line
        move_line = picking.move_lines[0]
        self.assertEqual(move_line.product_uom_qty, 1)
        move_line.product_uom_qty = 10
        self.assertEqual(move_line.product_uom_qty, 10)

        # Add a new line
        len_move_lines = len(picking.move_lines)
        self.add_move(picking)
        self.assertEqual(len(picking.move_lines), len_move_lines + 1)

        # Able to modificate the functional field value
        self.assertTrue(picking.change_picking)
        picking.change_picking = False
        self.assertFalse(picking.change_picking)

        # Duplicate Picking: The new picking have de True default value in
        # change_picking instead the value False in the original picking
        picking2 = picking.copy()
        self.assertTrue(picking2)
        self.assertTrue(picking2.change_picking)

        # Delete Picking:
        picking.unlink()
        picking2.unlink()
        self.assertFalse(picking.exists())
        self.assertFalse(picking2.exists())

    def test_02_picking_create_from_po(self):
        """Create a stock picking from a purchase order confirmation and checking
        that the picking inherit the purchase order id and change_picking
        attribute to False (By default a purchase order picking can not change
        its move lines).
        """
        # Create a purchase order and check that was created correctly. If
        # draft state with no lines and with chage_picking = False.
        order = self.create_po()
        self.assertTrue(order)
        self.assertEquals(order.state, 'draft')
        self.assertFalse(order.change_picking)
        self.assertFalse(order.order_line)

        # Add one order line
        self.create_pol(order)

        # Validate purchase order
        order.signal_workflow('purchase_confirm')
        self.assertEquals(order.state, 'approved')

        # Check picking was generated and have the purchase order related and
        # the change_picking attribute
        self.assertTrue(order.picking_ids)
        self.assertEqual(1, len(order.picking_ids))
        picking = order.picking_ids[0]
        self.assertEqual(picking.state, 'assigned')
        self.assertEqual(picking.purchase_id, order)
        self.assertEqual(picking.change_picking, order.change_picking)

    def test_03_picking_create_from_po_change_lines(self):
        """"""
        # Create a purchase order and then change the default change_picking =
        # False to True.
        order = self.create_po()
        self.assertTrue(order)
        self.assertEquals(order.state, 'draft')
        self.assertFalse(order.change_picking)
        order.change_picking = True
        self.assertTrue(order.change_picking)

        # Add one order line
        self.create_pol(order)

        # Validate purchase order
        order.signal_workflow('purchase_confirm')
        self.assertEquals(order.state, 'approved')

        # Check that the picking was generated and have the purchase order
        # related and the change_picking attribute
        self.assertTrue(order.picking_ids)
        self.assertEqual(1, len(order.picking_ids))
        picking = order.picking_ids[0]
        self.assertEqual(picking.state, 'assigned')
        self.assertEqual(picking.purchase_id, order)
        self.assertEqual(picking.change_picking, order.change_picking)
