# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Vauxoo
#    Author : Osval Reyes <osval@vauxoo.com>
#
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
#
##############################################################################
from openerp.tests.common import TransactionCase

class TestStockCardNegativeStock(TransactionCase):

    def setUp(self):
        super(TestStockCardNegativeStock, self).setUp()
        self.sc_product = self.env['stock.card.product']
        self.move = self.env['stock.move']
        self.quant = self.env['stock.quant']
        self.sale_order = self.env['sale.order']
        self.wizard = self.env['stock.transfer_details']
        self.wizard_item = self.env['stock.transfer_details_items']
        self.product_id = self.env.ref('stock_card.product01')

    def get_stock_valuations(self):
        return self.sc_product._stock_card_move_get(self.product_id.id)['res']

    def test_01_stock_card(self):
        card_lines = self.get_stock_valuations()
        self.assertEqual(len(card_lines), 12,
                         "Expected Stock Card lines is 12")

        self.assertEqual(card_lines[11]['average'], 38)
        self.assertEqual(card_lines[11]['material'], 38)
        self.assertEqual(card_lines[11]['landed'], 0.0)
        self.assertEqual(card_lines[11]['subcontracting'], 0.0)

    def modify_sgmnts(self):
        transactions = ['po_03_line_01', 'so_02_line_01']
        for trxname in transactions:
            quant_ids = self.move.search([('name', '=', trxname)]).\
                mapped('quant_ids.id')
            quant_id = self.quant.browse(max(quant_ids))
            quant_id.write({
                'material_cost': 64,
                'landed_cost': 16,
                'subcontracting_cost': 8,
            })

    def test_02_test_sgmnts(self):
        self.modify_sgmnts()
        card_lines = self.get_stock_valuations()
        self.assertEqual(len(card_lines), 12,
                         "Expected Stock Card lines is 12")

        self.assertEqual(card_lines[3]['average'], 60)
        self.assertEqual(card_lines[4]['average'], 60)
        self.assertEqual(card_lines[6]['average'], 64)
        self.assertEqual(card_lines[11]['average'], 38)

        # / ! \ check what's happening with material for this demo
        self.assertEqual(card_lines[3]['material'], 48)
        self.assertEqual(card_lines[4]['material'], 48)
        self.assertEqual(card_lines[6]['material'], 64)
        self.assertEqual(card_lines[11]['material'], 38)

        self.assertEqual(card_lines[3]['landed'], 8)
        self.assertEqual(card_lines[4]['landed'], 8)
        self.assertEqual(card_lines[6]['landed'], 0.0)
        self.assertEqual(card_lines[11]['landed'], 0.0)

        self.assertEqual(card_lines[3]['subcontracting'], 4)
        self.assertEqual(card_lines[4]['subcontracting'], 4)
        self.assertEqual(card_lines[6]['subcontracting'], 0.0)
        self.assertEqual(card_lines[11]['subcontracting'], 0.0)

    def create_sale_order(self, vals):
        qty = vals['qty']
        price = vals['cost']
        sale_order_id = self.sale_order.create({
            'partner_id': self.env.ref('base.res_partner_12').id,
            'client_order_ref': "Sale Order (qty=%s, price=%s)" % (
                str(qty), str(price)),
            'order_policy': 'manual',
            'order_line': [(0, 0, {
                'product_id': self.product_id.id,
                'product_uom_qty': qty,
                'price_unit': price,
            })]
        })

        sale_order_id.action_button_confirm()
        for picking_id in sale_order_id.picking_ids:
            picking_id.action_assign()
            picking_id.force_assign()
            picking_id.action_confirm()
            wizard_id = self.wizard.create({
                'picking_id': picking_id.id,
            })

            for move_id in picking_id.move_lines:
                self.wizard_item.create({
                    'transfer_id': wizard_id.id,
                    'product_id': move_id.product_id.id,
                    'quantity': move_id.product_qty,
                    'sourceloc_id': move_id.location_id.id,
                    'destinationloc_id': move_id.location_dest_id.id,
                    'product_uom_id': move_id.product_uom.id,
                })

            wizard_id.do_detailed_transfer()
            self.assertEqual(picking_id.state, 'done')
        return sale_order_id

    def test_03_antiquant(self):
        self.create_sale_order({'qty': 100, 'cost': 100})
        res = self.get_stock_valuations()
        last_line = res[-1]
        self.assertEqual(last_line['average'], 38)
        self.assertEqual(last_line['material'], 38)
        self.assertEqual(last_line['product_qty'], -97)
