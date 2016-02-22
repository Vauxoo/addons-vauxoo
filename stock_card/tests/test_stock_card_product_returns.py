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
from openerp.tools.float_utils import float_compare
from datetime import datetime, timedelta


class TestStockCardProductReturns(TransactionCase):

    def setUp(self):
        super(TestStockCardProductReturns, self).setUp()
        self.stock_card = self.env['stock.card']
        self.sc_product = self.env['stock.card.product']
        self.move = self.env['stock.move']
        self.product_id = self.env.ref('stock_card.product02')

        self.values = [
            ('sc_po_01', {'cost': 100, 'qty': 10, 'avg': 100, 'mov_val': 1000,
                          'inv_val': 1000}),
            ('sc_so_01', {'cost': 100, 'qty': 6, 'avg': 100, 'mov_val': -400,
                          'inv_val': 600}),
            ('sc_so_02', {'cost': 100, 'qty': 1, 'avg': 100, 'mov_val': -500,
                          'inv_val': 100}),
            ('sc_po_02', {'cost': 300, 'qty': 4, 'avg': 250, 'mov_val': 900,
                          'inv_val': 1000}),
            ('sc_so_03', {'cost': 250, 'qty': 1, 'avg': 250, 'mov_val': -750,
                          'inv_val': 250}),
            ('pick_01_sc_so_01', {'cost': 100, 'qty': 2, 'avg': 175,
                                  'mov_val': 100, 'inv_val': 350}),
            ('sc_po_03', {'cost': 220, 'qty': 7, 'avg': 207.14,
                          'mov_val': 1100, 'inv_val': 1450}),
            ('sc_po_04', {'cost': 400, 'qty': 10, 'avg': 265, 'mov_val': 1200,
                          'inv_val': 2650}),
            ('pick_02_sc_po_03', {'cost': 220, 'qty': 8, 'avg': 276.25,
                                  'mov_val': -440, 'inv_val': 2210}),
        ]

        # separate in time all transactions
        delta = 0
        for k, v in self.values:
            obj = self.env.ref('stock_card.'+k)
            move_ids = {}
            if k.startswith('sc_'):
                move_ids = obj.picking_ids.mapped('move_lines')
            elif k.startswith('pick_'):
                move_ids = obj.move_lines
            for move_id in move_ids:
                delta += 1
                next_hour = datetime.strptime(
                    '2016-01-01 01:00:00',
                    '%Y-%m-%d %H:%M:%S') + timedelta(hours=delta)
                move_id.write({'date': next_hour})

    def get_stock_valuations(self, product_id):
        sc_moves = self.sc_product._stock_card_move_get(
            product_id)
        return sc_moves['res']

    def test_01_do_inouts(self):
        card_lines = self.get_stock_valuations(self.product_id.id)
        self.assertEqual(len(self.values), len(card_lines),
                         "Both lists should have the same length(=9)")
        for succeed, expected in zip(card_lines, self.values):
            origin = self.env['stock.move'].browse(succeed['move_id']).origin
            name, expected = expected
            self.assertEqual(origin, name,
                             "Transactions aren't in the same order")

            self.assertEqual(0, float_compare(expected['avg'],
                                              succeed['average'],
                                              precision_rounding=1),
                             "Average Cost current={0} expected={1} is not "
                             "the expected: {2}".
                             format(succeed['average'],
                                    expected['avg'], expected))

            self.assertEqual(expected['cost'],
                             succeed['cost_unit'],
                             "Unit Cost current={0} expected={1} is not "
                             "the expected: {2}".
                             format(succeed['cost_unit'],
                                    expected['cost'], expected))

            self.assertEqual(0, float_compare(expected['inv_val'],
                                              succeed['inventory_valuation'],
                                              precision_rounding=1),
                             "Inventory Value current={0} expected={1} is not "
                             "match: {2}".
                             format(succeed['inventory_valuation'],
                                    expected['inv_val'], expected))

            self.assertEqual(0, float_compare(expected['mov_val'],
                                              succeed['move_valuation'],
                                              precision_rounding=1),
                             "Movement Value current={0} expected={1} is not "
                             "match: {2}".
                             format(succeed['move_valuation'],
                                    expected['mov_val'], expected))
