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


class TestStockCard(TransactionCase):

    def setUp(self):
        super(TestStockCard, self).setUp()
        self.stock_card = self.env['stock.card']
        self.sc_product = self.env['stock.card.product']
        self.sc_move = self.env['stock.card.move']
        self.product_targus_id = self.env.ref('stock_card.product_targus_a')
        pass

    def test_01_stock_card(self):
        sc_product_id = self.sc_product.create({
            'product_id': self.product_targus_id.id
        })
        self.assertTrue(sc_product_id.id)
        res = sc_product_id.stock_card_move_get()
        self.assertTrue(res)

        sc_product_id.stock_card_move_get()
        moves = sc_product_id.action_view_moves()

        # assert domains exists into moves
        sc_move_domain_id = eval(moves['domain'])[0][2][0]
        self.assertTrue(sc_move_domain_id)

        # assert that stock.card.move exists
        self.sc_move_id = self.sc_move.browse([sc_move_domain_id])
        self.assertTrue(len(self.sc_move_id) > 0)
        self.assertTrue(self.sc_move_id.stock_card_product_id.product_id.id,
                        self.product_targus_id.id)

        # assert average cost
        self.assertEqual(self.sc_move_id.average,
                         sc_product_id.product_id.standard_price)
