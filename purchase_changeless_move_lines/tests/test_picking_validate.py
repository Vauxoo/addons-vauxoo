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

from openerp import exceptions
from openerp.addons.purchase_changeless_move_lines.tests.common \
    import TestStockCommon


class TestPickingValidate(TestStockCommon):

    """Test picking validation taking the picking create from a purchase order
    confirmation
    """

    def setUp(self):
        """Add global varaible for the model and xml id record used in this test
        """
        super(TestPickingValidate, self).setUp()

    def test_01_base(self):
        """Validate a picking from a purchase order making not changes to the
        picking moves and with a purchase order change_picking False.
        """
        # Create/validate PO
        order = self.create_and_validate_po()

        # Validate picking
        picking = order.picking_ids[0]
        picking.do_transfer()
        self.assertEqual(picking.state, 'done')

    def test_02_add_move(self):
        """Validate a picking generate via purchase order (w/change_picking False)
        adding one move to picking. This will fail and raise and exception
        indicating this is not possible.
        """
        # Create/validate PO
        order = self.create_and_validate_po()

        # Add new move in picking
        picking = order.picking_ids[0]
        self.add_move(picking)

        # Try to validate picking
        self.assertEqual(picking.state, 'draft')
        with self.assertRaisesRegexp(exceptions.Warning, 'NEW move'):
            picking.do_transfer()
        self.assertEqual(picking.state, 'draft')

    def test_03_edit_move(self):
        """Validate a picking generate via purchase order (w/change_picking False)
        editing the product or qty on the move. This will fail and raise
        and exception indicating this is not possible.
        """
        # Create/validate PO
        order = self.create_and_validate_po()

        # Edit move qty
        picking = order.picking_ids[0]
        move = picking.move_lines[0]
        self.assertEqual(move.product_uom_qty, 10)
        move.write({'product_uom_qty': '3'})
        self.assertEqual(move.product_uom_qty, 3)

        # Try to validate picking
        self.assertEqual(picking.state, 'assigned')
        with self.assertRaisesRegexp(exceptions.Warning, 'EDITED move'):
            picking.do_transfer()
        self.assertEqual(picking.state, 'assigned')

    def test_04_remove_move(self):
        """Validate a picking generate via purchase order (w/change_picking False)
        remove one move. This will fail and raise and exception indicating
        this is not possible.
        """
        # Create/validate PO
        order = self.create_and_validate_po()

        # Validate PO and check generate picking with two moves.
        order.signal_workflow('purchase_confirm')
        self.assertTrue(order.picking_ids)
        picking = order.picking_ids[0]
        self.assertEqual(len(picking.move_lines), 2)

        # Remove one move from picking.
        self.remove_move(picking)
        self.assertEqual(len(picking.move_lines), 1)

        # Try to validate picking
        self.assertEqual(picking.state, 'assigned')
        with self.assertRaisesRegexp(exceptions.Warning, 'REMOVE move'):
            picking.do_transfer()
        self.assertEqual(picking.state, 'assigned')
