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


class TestPurchaseOrder(TestStockCommon):

    def setUp(self):
        super(TestPurchaseOrder, self).setUp()

    def test_01_po(self):
        """Purchase Order CRUD: Create, Read, Update, Duplicate, and Delete
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

        # Duplicate Purchase Order: The change_picking field must be default
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
