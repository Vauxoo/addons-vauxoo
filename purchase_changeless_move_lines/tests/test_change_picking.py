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

from openerp.tests import common
import time


class TestChangePicking(common.TransactionCase):

    def setUp(self):
        """
        Add global varaible for the model and xml id record used in this test
        """
        super(TestChangePicking, self).setUp()
        self.product = self.ref('product.product_product_4')
        self.partner = self.ref('base.res_partner_1')
        self.location = self.ref('stock.stock_location_stock')
        self.supp_location = self.ref('stock.stock_location_suppliers')
        self.picking_type_in = self.ref('stock.picking_type_in')
        self.order_obj = self.env['purchase.order']
        self.product_obj = self.env['product.product']
        self.picking_obj = self.env['stock.picking']

    def create_pol(self, order, product):
        """
        Create a new purchase order line for the given purchase order taking
        as input only the product
        """
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

    def test_01_picking_create(self):
        """
        Create a stock picking manually and check it was correctly created
        with no purchase_id releated and by default the move lines can be
        modificated (change_picking = True).
        """
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

    def test_02_picking_create_from_po(self):
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
        product = self.product_obj.browse(self.product)
        self.create_pol(order, product)
        self.assertTrue(order.order_line)
        self.assertEquals(len(order.order_line), 1)
        self.assertIn(product, order.order_line.mapped('product_id'))

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
        """
        """
        # Create a purchase order and then change the default change_picking =
        # False to True.
        order = self.create_po()
        self.assertTrue(order)
        self.assertFalse(order.change_picking)
        order.change_picking = True
        self.assertTrue(order.change_picking)

        # Add one order line
        product = self.product_obj.browse(self.product)
        self.create_pol(order, product)

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
