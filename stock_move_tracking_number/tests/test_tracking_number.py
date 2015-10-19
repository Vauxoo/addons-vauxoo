# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Katherine Zaoral <kathy@vauxoo.com>
#    planned by: Rafael Silva <rsilvam@vauxoo.com>
############################################################################

from openerp.tests import common
from openerp.exceptions import ValidationError


class TestTrackingNumber(common.TransactionCase):

    def setUp(self):
        super(TestTrackingNumber, self).setUp()
        self.move_obj = self.env['stock.move']
        self.picking_obj = self.env['stock.picking']
        self.wiz_obj = self.env['wizard.modify.tracking.number']

    def create_picking(self):
        """ Utility to create pickings during the test.
        """
        values = {
            'origin': 'SMTN Picking Test',
            'picking_type_id': self.ref('stock.picking_type_in'),
            'partner_id': self.ref('base.res_partner_3'),
        }
        picking = self.picking_obj.create(values)
        self.assertTrue(picking)
        return picking

    def create_move(self, picking=False):
        """ Utility to create moves during the test.
        """
        values = {
            'name': 'SMTN Test Move',
            'picking_type_id': self.ref('stock.picking_type_in'),
            'product_id': self.ref('product.product_product_4'),
            'product_uom': self.ref('product.product_uom_unit'),
            'product_uom_qty': 500,
            'location_id': self.ref('stock.stock_location_suppliers'),
            'location_dest_id': self.ref('stock.stock_location_stock'), }
        if picking:
            values.update(picking_id=picking.id)
        move = self.move_obj.create(values)
        return move

    def test_01(self):
        """ Basic CRUD stock move
        """
        # Create
        move = self.create_move()
        self.assertEqual(move.state, 'draft')

        # Read (via ORM)
        move.read([])

        # Read (via direct)
        self.assertTrue(move.name)
        self.assertFalse(move.tracking_number)

        # Write
        move.tracking_number = '123456'

        # Copy
        move2 = move.copy()
        self.assertTrue(move2)

        # Delete
        self.assertTrue(move.exists())
        move.unlink()
        self.assertFalse(move.exists())

    def test_02(self):
        """ Constraint: Try to set the tracking number in a done stock move.
        """
        move = self.create_move()
        move.action_done()
        self.assertEqual(move.state, 'done')

        msg_error = 'The tracking number can not be modify in a done move'
        with self.assertRaisesRegexp(ValidationError, msg_error):
            move.tracking_number = '12345'

    def test_03(self):
        """ Modify Tracking Number Wizard
        """
        # Create a stock picking with multiple move lines
        picking = self.create_picking()
        move1 = self.create_move(picking=picking)
        move2 = self.create_move(picking=picking)

        # Check that all the move lines are not done
        self.assertEqual(move1.state, 'draft')
        self.assertEqual(move2.state, 'draft')

        # Check that all the move lines have empty tracking number
        self.assertFalse(move1.tracking_number)
        self.assertFalse(move2.tracking_number)

        # Run wizard (simulate run from picking form view).
        new_tracking_number = '123456'
        wiz = self.wiz_obj.with_context({
            'active_model': 'stock.picking',
            'active_id': picking.id,
            'active_ids': [picking.id],
        }).create({'tracking_number': new_tracking_number})
        self.assertTrue(wiz)
        self.assertTrue(wiz.lines)
        wiz.modify()

        # Check that all the move line were set with the tracking number.
        self.assertEqual(move1.tracking_number, new_tracking_number)
        self.assertEqual(move2.tracking_number, new_tracking_number)
