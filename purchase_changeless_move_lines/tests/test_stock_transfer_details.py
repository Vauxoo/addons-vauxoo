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


class TestStockTransferDetails(TestStockCommon):

    """Picking Validation via Stock Transfer Detail Wizard.
    """

    def setUp(self):
        """Add global varaible for the model and xml id record used in this test
        """
        super(TestStockTransferDetails, self).setUp()
        self.wiz_obj = self.env['stock.transfer_details']

    def add_transfer_item(self, wiz):
        """Add new transfer item line to the stock transfer details wizard.
        """
        product = self.product_obj.browse(self.product3)
        wiz.write({
            'item_ids': [(0, 0, {
                'product_id': product.id,
                'quantity': 6.0,
                'product_uom_id': product.uom_id.id,
                'sourceloc_id': self.supp_location,
                'destinationloc_id': self.location,
            })]
        })

    def remove_transfer_item(self, wiz):
        """Add new transfer item line to the stock transfer details wizard.
        """
        item = wiz.item_ids.filtered(
            lambda line: line.product_id.id == self.product2)
        wiz.write({'item_ids': [(3, item.id)]})

    def test_01_manual(self):
        """Create stock transfer detauks wizard by hand (manually).
        """
        # Create/validate PO
        order = self.create_and_validate_po()

        # Create a transfer details wizard.
        picking = order.picking_ids[0]
        wiz = self.wiz_obj.with_context({
            'active_id': picking.id,
            'active_ids': [picking.id],
            'active_model': 'stock.picking'
        }).create({'picking_id': picking.id})
        self.assertTrue(wiz)
        self.assertTrue(wiz.item_ids)
        self.assertEqual(len(wiz.item_ids), 2)

        # Validate picking
        self.assertEqual(picking.state, 'assigned')
        wiz.do_detailed_transfer()
        self.assertEqual(picking.state, 'done')

    def test_02_wizard(self):
        """This simaluate the picking Transfer via interface. When the user click
        the Transfer button and the Enter Transfer Detail wizard show up. In
        this case no line change in purchase order, picking or transfer wizard.
        """
        # Create/validate PO
        order = self.create_and_validate_po()

        # Create a transfer details wizard.
        picking = order.picking_ids[0]
        view = picking.do_enter_transfer_details()

        # Validate picking
        self.assertEqual(picking.state, 'assigned')
        self.wiz_obj.browse(view.get('res_id')).do_detailed_transfer()
        self.assertEqual(picking.state, 'done')

    def test_03_add_move(self):
        """This simaluate the picking Transfer via interface. When the user click
        the Transfer button and the Enter Transfer Detail wizard show up. In
        this case will add a picking line before call the wizard. This must be
        fail.
        """
        # Create/validate PO
        order = self.create_and_validate_po()
        picking = order.picking_ids[0]

        # Add new move to picking
        self.assertEqual(len(picking.move_lines), 2)
        self.add_move(picking)
        self.assertEqual(len(picking.move_lines), 3)

        # Try to validate the picking calling the Transfer wizard. Will fail
        # becuase a move was added when the purchase order have
        # change_picking False.
        self.assertEqual(picking.state, 'draft')
        with self.assertRaisesRegexp(exceptions.Warning, 'NEW move'):
            picking.do_enter_transfer_details()
        self.assertEqual(picking.state, 'draft')

    def test_04_remove_move(self):
        """This simaluate the picking Transfer via interface. When the user click
        the Transfer button and the Enter Transfer Detail wizard show up. In
        this case will add a picking line before call the wizard. This must be
        fail.
        """
        # Create/validate PO
        order = self.create_and_validate_po()
        picking = order.picking_ids[0]

        # Remove one move from picking.
        self.assertEqual(len(picking.move_lines), 2)
        self.remove_move(picking)
        self.assertEqual(len(picking.move_lines), 1)

        # Try to validate the picking calling the Transfer wizard. Will fail
        # becuase a move was removed when the purchase order have
        # change_picking False.
        self.assertEqual(picking.state, 'assigned')
        with self.assertRaisesRegexp(exceptions.Warning, 'REMOVE move'):
            picking.do_enter_transfer_details()
        self.assertEqual(picking.state, 'assigned')

    def test_05_edit_move(self):
        """This simaluate the picking Transfer via interface. When the user click
        the Transfer button and the Enter Transfer Detail wizard show up. In
        this case will edit a picking line before call the wizard. This must be
        fail.
        """
        # Create/validate PO
        order = self.create_and_validate_po()
        picking = order.picking_ids[0]

        # Edit move
        move = picking.move_lines.filtered(
            lambda line: line.product_id.id == self.product)
        self.assertEqual(move.product_uom_qty, 10.0)
        move.product_uom_qty = 5.0
        self.assertEqual(move.product_uom_qty, 5.0)

        # Try to validate the picking calling the Transfer wizard. Will fail
        # becuase a move was removed when the purchase order have
        # change_picking False.
        self.assertEqual(picking.state, 'assigned')
        with self.assertRaisesRegexp(exceptions.Warning, 'EDITED move'):
            picking.do_enter_transfer_details()
        self.assertEqual(picking.state, 'assigned')

    def test_06_add_transfer_item(self):
        """This simaluate the picking Transfer via interface. When the user click
        the Transfer button and the Enter Transfer Detail wizard show up. In
        this case will add a picking line before call the wizard. This must be
        fail.
        """
        # Create/validate PO
        order = self.create_and_validate_po()
        picking = order.picking_ids[0]

        # Create Transfer wizard
        view = picking.do_enter_transfer_details()
        wiz = self.wiz_obj.browse(view.get('res_id'))

        # Add transfer item
        self.add_transfer_item(wiz)

        # Try to validate the picking calling the Transfer wizard. Will fail
        # becuase a transfer line was added.
        self.assertEqual(picking.state, 'assigned')
        with self.assertRaisesRegexp(exceptions.Warning, 'DIFFER move'):
            wiz.do_detailed_transfer()

    def test_07_remove_transfer_item(self):
        """This simaluate the picking Transfer via interface. When the user click
        the Transfer button and the Enter Transfer Detail wizard show up. In
        this case will remove a picking line before call the wizard. This must
        be fail.
        """
        # Create/validate PO
        order = self.create_and_validate_po()
        picking = order.picking_ids[0]

        # Create Transfer wizard
        view = picking.do_enter_transfer_details()
        wiz = self.wiz_obj.browse(view.get('res_id'))

        # Remove transfer item
        self.remove_transfer_item(wiz)

        # Try to validate the picking calling the Transfer wizard. Will fail
        # becuase a transfer line was added.
        # self.assertEqual(picking.state, 'assigned')
        with self.assertRaisesRegexp(exceptions.Warning, 'REMOVE move'):
            wiz.do_detailed_transfer()
        self.assertEqual(picking.state, 'assigned')

        # TODO add test transfer wizard edit transfer item
