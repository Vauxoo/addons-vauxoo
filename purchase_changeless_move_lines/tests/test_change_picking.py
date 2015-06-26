# -*- encoding: utf-8 -*-
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

from openerp import exceptions
from openerp.tests import common
import time


class TestChangePicking(common.TransactionCase):

    def setUp(self):
        """
        Add global varaible for the model and xml id record used in this test
        """
        super(TestChangePicking, self).setUp()
        self.product = self.ref('product.product_product_4')
        self.product2 = self.ref('product.product_product_35')
        self.partner = self.ref('base.res_partner_1')
        self.location = self.ref('stock.stock_location_stock')
        self.supp_location = self.ref('stock.stock_location_suppliers')
        self.picking_type_in = self.ref('stock.picking_type_in')
        self.order_obj = self.env['purchase.order']
        self.product_obj = self.env['product.product']
        self.picking_obj = self.env['stock.picking']

    def create_pol(self, order, product=False):
        """
        Create a new purchase order line for the given purchase order taking
        as input only the product
        """
        product = self.product_obj.browse(product or self.product)
        order.write({
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_qty': 10.0,
                'product_uom': product.uom_id.id,
                'price_unit': product.price,
                'name': product.name_template,
                'date_planned': time.strftime('%Y-%m-%d'),
            })]})

    def create_po(self, invoice_method='picking'):
        """ Create a purchase order """
        order = self.order_obj.create({
            'partner_id': self.partner,
            'location_id': self.location,
            'pricelist_id': 1,
            'invoice_method': invoice_method,
        })
        return order

    def add_move_line(self, picking):
        """ add new line to the picking """
        product = self.product_obj.browse(self.product2)
        picking.write({'move_lines': [(0, 0, {
            'name': product.name,
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': 3,
            'location_id': self.supp_location,
            'location_dest_id': self.location,
        })]})

    def create_and_validate_po(self):
        """ Create and Validate purchase order """
        order = self.create_po()
        self.create_pol(order)
        order.signal_workflow('purchase_confirm')
        return order

    def test_01_po(self):
        """
        Purchase Order CRUD: Create, Read, Update, Duplicate, and Delete
        """
        # Create Purchase Order: Check that was created correctly in draft
        # state with no lines and with change_picking = False.
        order = self.create_po()
        self.assertTrue(order)
        self.assertEquals(order.state, 'draft')
        self.assertFalse(order.change_picking)
        self.assertFalse(order.order_line)

        # Update Purchase Order: Add one order line and also modificate the
        # default value change_picking = True
        self.create_pol(order)
        self.assertTrue(order.order_line)
        self.assertEquals(len(order.order_line), 1)
        self.assertIn(self.product, order.order_line.mapped('product_id.id'))

        # Duplicate Purchase Order: The change_picking field mut be default
        # False (First change purchase order to True to see the difference).
        order.change_picking = True
        self.assertTrue(order.change_picking)
        order2 = order.copy()
        self.assertTrue(order2)
        self.assertEquals(order2.state, 'draft')
        self.assertTrue(order2.change_picking)

        # Delete Purchase Order
        order.unlink()
        order2.unlink()
        self.assertFalse(order.exists())
        self.assertFalse(order2.exists())

    def test_02_picking(self):
        """
        Stock Picking CRUD: Create, Read, Update, Duplicate, and Delete
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
        self.add_move_line(picking)
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

    def test_03_picking_create_from_po(self):
        """
        Create a stock picking from a purchase order confirmation and checking
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

    def test_04_picking_create_from_po_change_lines(self):
        """
        """
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

    def test_05_picking_validate(self):
        """
        Validate a picking from a purchase order making not change to the
        picking move lines and with a purchase order change_picking False.
        """
        # Create/validate PO
        order = self.create_and_validate_po()

        # Validate picking
        picking = order.picking_ids[0]
        picking.do_transfer()
        self.assertEqual(picking.state, 'done')

    def test_06_picking_validate_add_lines(self):
        """
        Validate a picking generate via purchase order (w/change_picking False)
        adding one move line to picking. This will fail and raise and exception
        indicating this is not possible.
        """
        # Create/validate PO
        order = self.create_and_validate_po()

        # Add new move line in picking.
        picking = order.picking_ids[0]
        self.add_move_line(picking)

        # Try to validate picking
        self.assertEqual(picking.state, 'draft')
        with self.assertRaisesRegexp(exceptions.Warning, 'NEW move lines'):
            picking.do_transfer()
        self.assertEqual(picking.state, 'draft')

    def test_07_picking_validate_edit_line(self):
        """
        Validate a picking generate via purchase order (w/change_picking False)
        editing the product or qty on the move line. This will fail and raise
        and exception indicating this is not possible.
        """
        # Create/validate PO
        order = self.create_and_validate_po()

        # Edit move line qty
        picking = order.picking_ids[0]
        move_line = picking.move_lines[0]
        self.assertEqual(move_line.product_uom_qty, 10)
        move_line.write({'product_uom_qty': '3'})
        self.assertEqual(move_line.product_uom_qty, 3)

        # Try to validate picking
        self.assertEqual(picking.state, 'assigned')
        with self.assertRaisesRegexp(exceptions.Warning, 'DIFFERENT move lin'):
            picking.do_transfer()
        self.assertEqual(picking.state, 'assigned')

    def test_08_picking_validate_rem_lines(self):
        """
        Validate a picking generate via purchase order (w/change_picking False)
        remove one move line. This will fail and raise and exception indicating
        this is not possible.
        """
        # Create PO with 2 lines
        order = self.create_po()
        self.create_pol(order)
        self.create_pol(order, self.product2)
        self.assertEqual(len(order.order_line), 2)

        # Validate PO and check generate picking with two move lines.
        order.signal_workflow('purchase_confirm')
        picking = order.picking_ids[0]
        self.assertEqual(len(picking.move_lines), 2)

        # Remove one line from picking.
        move_line2 = picking.move_lines[1]
        picking.write({'move_lines': [(3, move_line2.id)]})
        self.assertEqual(len(picking.move_lines), 1)

        # Try to validate picking
        self.assertEqual(picking.state, 'assigned')
        with self.assertRaisesRegexp(exceptions.Warning, 'REMOVE move lines'):
            picking.do_transfer()
        self.assertEqual(picking.state, 'assigned')
