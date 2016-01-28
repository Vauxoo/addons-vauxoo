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

        self.product_id = self.env.ref('stock_card.product01')

    def get_stock_valuations(self):
        sc_moves = self.sc_product._stock_card_move_get(
            self.product_id.id, return_values=True)
        return sc_moves['res']

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
