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
from openerp.tools.safe_eval import safe_eval
from openerp.exceptions import Warning as UserError


class TestStockCard(TransactionCase):

    def setUp(self):
        super(TestStockCard, self).setUp()
        self.stock_card = self.env['stock.card']
        self.sc_product = self.env['stock.card.product']
        self.sc_move = self.env['stock.card.move']
        self.move = self.env['stock.move']
        self.product_id = self.env.ref('stock_card.product01')

        self.inv_ids = [
            {
                'cost': 20,
                'qty': 2,
                'write': True,
                'expected_avg': 20,
                'theoretical_qty': 0,
            },
            {
                'cost': 40,
                'qty': 5,
                'write': True,
                'expected_avg': 32,
                'theoretical_qty': 2,
            },
            {
                'cost': 32,
                'qty': 4,
                'write': False,
                'expected_avg': 32,
                'theoretical_qty': 5,
            },
            {
                'cost': 64,
                'qty': 8,
                'write': True,
                'expected_avg': 48,
                'theoretical_qty': 4,
            },
            {
                'cost': 48,
                'qty': 4,
                'write': False,
                'expected_avg': 48,
                'theoretical_qty': 8,
            },
        ]

    def test_00_stock_card_from_product(self):
        self.assertEqual(
            self.stock_card._get_fieldnames(), {'average': 'standard_price'},
            "It's required to stock.card have defined 'average' field mapping")

        res = {}
        msg_error = 'Asked Product has not Moves to show'
        with self.assertRaisesRegexp(UserError, msg_error):
            res = self.product_id.stock_card_move_get()

        self.test_01_stock_card()
        res = self.product_id.stock_card_move_get()
        res = safe_eval(res['domain'])[0][2]
        self.assertEqual(len(res), 6, 'Stock Card in this case have to be =5')

    def test_01_stock_card(self):
        for val in self.inv_ids:
            inv_id = self.create_inventory(self.product_id, val['qty'])
            inv_id.action_done()

        sc_product_id = self.sc_product.create({
            'product_id': self.product_id.id
        })
        self.assertTrue(sc_product_id.id)
        res = sc_product_id.stock_card_move_get()
        self.assertTrue(res)

        sc_product_id.stock_card_move_get()
        moves = sc_product_id.action_view_moves()

        # assert domains exists into moves
        sc_move_domain_id = safe_eval(moves['domain'])[0][2][0]
        self.assertTrue(sc_move_domain_id)

        # assert that stock.card.move exists
        self.sc_move_id = self.sc_move.browse([sc_move_domain_id])
        self.assertTrue(len(self.sc_move_id) > 0)
        self.assertTrue(self.sc_move_id.stock_card_product_id.product_id.id,
                        self.product_id.id)

        # assert average cost
        self.assertEqual(self.sc_move_id.average,
                         sc_product_id.product_id.standard_price)

    def test_02_check_inventory_initializations(self):
        moves = self.move.search([('product_id', '=', self.product_id.id)])

        for val in self.inv_ids:
            inv_id = self.create_inventory(self.product_id, val['qty'])
            inv_id.action_done()

        sc_product_id = self.sc_product.create({
            'product_id': self.product_id.id
        })

        sc_product_id.stock_card_move_get()
        moves = sc_product_id.action_view_moves()

        search_domain = safe_eval(moves['domain'])

        averages = self.sc_move.search(search_domain).mapped('average')
        costs = self.sc_move.search(search_domain).mapped('cost_unit')

        self.assertTrue(all(averages))
        self.assertTrue(all(costs))
        self.assertEqual(sum(averages), 100)
        self.assertEqual(sum(costs), 100)

    def create_inventory(self, product_id=False, product_qty=False):
        inv = self.env['stock.inventory']
        invline = self.env['stock.inventory.line']
        location_id = self.env.ref('stock.stock_location_stock')

        inventory_id = inv.create({
            'name': 'Inventory Adjustment',
            'filter': product_id and 'product' or 'none',
            'product_id': product_id.id,
        })

        invline.create({
            'inventory_id': inventory_id.id,
            'product_id': product_id.id,
            'product_qty': product_qty,
            'location_id': location_id.id,
        })

        inventory_id.prepare_inventory()

        return inventory_id
