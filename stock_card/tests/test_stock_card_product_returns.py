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
from datetime import datetime


class TestStockCardProductReturns(TransactionCase):

    def setUp(self):
        super(TestStockCardProductReturns, self).setUp()
        self.stock_card = self.env['stock.card']
        self.sc_product = self.env['stock.card.product']
        self.move = self.env['stock.move']
        self.product_id = self.env.ref('stock_card.product01')

        self.values = [
            {
                'name': 'po_01', 'cost': 32, 'qty': 2,
                'avg': 20, 'mov_val': 40, 'inv_val': 40
            },
            {
                'name': 'so_01', 'cost': 32, 'qty': 3,
                'avg': 32, 'mov_val': 120, 'inv_val': 160
            },
            {
                'name': 'so_02', 'cost': 32, 'qty': 1,
                'avg': 32, 'mov_val': -32, 'inv_val': 128
            },
            {
                'name': 'po_02', 'cost': 88, 'qty': 4,
                'avg': 60, 'mov_val': 352, 'inv_val': 480
            },
            {
                'name': 'so_03', 'cost': 60, 'qty': 7,
                'avg': 60, 'mov_val': -420, 'inv_val': 60
            },
            {
                'name': 'pick_01_so_01', 'cost': 62, 'qty': 2,
                'avg': 64, 'mov_val': -124, 'inv_val': -64
            },
            {
                'name': 'po_03', 'cost': 64, 'qty': 4,
                'avg': 64, 'mov_val': 256, 'inv_val': 192
            },
            {
                'name': 'pick_02_po_01', 'cost': 51, 'qty': 6,
                'avg': 38, 'mov_val': -306, 'inv_val': -114
            },
        ]

    def get_stock_valuations(self, product_id):
        sc_moves = self.sc_product._stock_card_move_get(
            product_id.id, return_values=True)
        return sc_moves['res']

    def test_01_do_inouts(self):
        card_lines = self.get_stock_valuations(self.product_id.id)

        self.assertEqual(len(self.values), len(card_lines),
                         "Both lists should have the same length(=8)")
        for expected, succeded in zip(self.values, card_lines):

            self.assertEqual(expected['avg'],
                             succeded['average'],
                             "Average Cost {0} is not the expected".
                             format(expected))

            self.assertEqual(expected['cost'],
                             succeded['cost_unit'],
                             "Unit Cost {0} is not the expected".
                             format(expected))

            self.assertEqual(expected['inv_val'],
                             succeded['inventory_valuation'],
                             "Inventory Value {0} does not match".
                             format(expected))

            self.assertEqual(expected['move_val'],
                             succeded['move_valuation'],
                             "Movement Value {0} does not match".
                             format(expected))
