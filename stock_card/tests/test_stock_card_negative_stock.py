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


class TestStockCardNegativeStock(TransactionCase):

    def setUp(self):
        super(TestStockCardNegativeStock, self).setUp()
        self.stock_card = self.env['stock.card']
        self.sc_product = self.env['stock.card.product']
        self.sc_move = self.env['stock.card.move']
        self.move = self.env['stock.move']
        self.product_id = self.env.ref('stock_card.product01')
        self.location_id = self.env.ref('stock.stock_location_stock')
        self.partner_id = self.env.ref('base.res_partner_23')
        self.purchase_order = self.env['purchase.order']
        self.wizard = self.env['stock.transfer_details']
        self.wizard_item = self.env['stock.transfer_details_items']
        self.transfer_details = self.env['stock.transfer_details']
        self.sale_order = self.env['sale.order']
        self.inv_ids = [
            {  # 1
                'do_purchase': True, 'cost': 20, 'qty': 2,
                'avg': 20, 'move_value': 40, 'inv_value': 40,
            },
            {  # 2
                'do_purchase': True, 'cost': 40, 'qty': 3,
                'avg': 32, 'move_value': 120, 'inv_value': 160,
            },
            {  # 3
                'do_purchase': False, 'cost': 32, 'qty': 1,
                'avg': 32, 'move_value': -32, 'inv_value': 128,
            },
            {  # 4
                'do_purchase': True, 'cost': 88, 'qty': 4,
                'avg': 60, 'move_value': 352, 'inv_value': 480,
            },
            {  # 5
                'do_purchase': False, 'cost': 60, 'qty': 7,
                'avg': 60, 'move_value': -420, 'inv_value': 60,
            },
            {  # 6
                'do_purchase': False, 'cost': 60, 'qty': 2,
                'avg': 60, 'move_value': -124, 'inv_value': -64,
            },
            {  # 7
                'do_purchase': True, 'cost': 64, 'qty': 4,
                'avg': 64, 'move_value': 256, 'inv_value': 192,
            },
            {  # 8
                'do_purchase': False, 'cost': 64, 'qty': 6,
                'avg': 64, 'move_value': 306, 'inv_value': -114,
            },
            {  # 9
                'do_purchase': False, 'cost': 64, 'qty': 2,
                'avg': 64, 'move_value': 76, 'inv_value': -190,
            },
            {  # 10
                'do_purchase': True, 'cost': 48, 'qty': 2,
                'avg': 48, 'move_value': 96, 'inv_value': -94,
            },
            {  # 11
                'do_purchase': True, 'cost': 56, 'qty': 2,
                'avg': 52, 'move_value': 112, 'inv_value': 18,
            },
            {  # 12
                'do_purchase': True, 'cost': 24, 'qty': 4,
                'avg': 38, 'move_value': 96, 'inv_value': 114,
            },
        ]

    def do_picking(self, picking_id=False):
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

    def create_purchase_order(self, qty=False, cost=False):
        purchase_order_id = self.purchase_order.create({
            'partner_id': self.partner_id.id,
            'location_id': self.ref('stock.stock_location_stock'),
            'pricelist_id': self.ref('purchase.list0'),
            'order_line': [(0, 0, {
                'name': "{0} (qty={1}, cost={2})".format(self.product_id.name,
                                                         qty, cost),
                'product_id': self.product_id.id,
                'price_unit': cost,
                'product_qty': qty,
                'date_planned': datetime.now().strftime('%Y-%m-%d'),
            })]
        })

        purchase_order_id.wkf_confirm_order()
        purchase_order_id.action_invoice_create()
        purchase_order_id.action_picking_create()
        self.do_picking(purchase_order_id.picking_ids[0])

    def create_sale_order(self, qty=False, price=False):
        sale_order_id = self.sale_order.create({
            'partner_id': self.partner_id.id,
            'client_order_ref': "Sale Order (qty={0}, price={1})".format(
                str(qty), str(price)),
            'order_policy': 'manual',
            'order_line': [(0, 0, {
                'product_id': self.product_id.id,
                'product_uom_qty': qty,
                'price_unit': price,
            })]
        })

        sale_order_id.action_button_confirm()
        self.do_picking(sale_order_id.picking_ids[0])
        return sale_order_id

    def get_last_stock_valuation(self):
        sc_product_id = self.sc_product.create({
            'product_id': self.product_id.id
        })

        sc_product_id.stock_card_move_get()
        sc_move_id = self.env['stock.card.move'].browse(
            max(eval(sc_product_id.action_view_moves()['domain'])[0][2]))
        return sc_move_id.move_valuation, sc_move_id.inventory_valuation

    def test_01_do_inouts(self):

        for expected in self.inv_ids:
            qty = expected['qty']
            costprice = expected['cost']

            if expected['do_purchase']:
                self.product_id.write({
                    'standard_price': expected['cost']
                })
                self.create_purchase_order(qty=qty, cost=costprice)
            else:
                self.create_sale_order(qty=qty, price=costprice)

            sc_product_id = self.sc_product.create({
                'product_id': self.product_id.id
            })

            sc_product_id.stock_card_move_get()
            retrieved_avg = sc_product_id.get_average(self.product_id.id)
            self.assertEqual(expected['avg'], retrieved_avg,
                             "AVG Cost is not the expected")
            move_value, inv_value = self.get_last_stock_valuation()

            index = self.inv_ids.index(expected)+1
            self.assertEqual(inv_value, expected['inv_value'],
                             "Inventory Value #{0} does not match".
                             format(index))
            self.assertEqual(move_value, expected['move_value'],
                             "Movement Value #{0} does not match".
                             format(index))
