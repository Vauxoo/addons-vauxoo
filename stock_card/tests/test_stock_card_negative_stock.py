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
import logging
from tabulate import tabulate
import pandas as pd

from openerp.tests.common import TransactionCase
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


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
        self.delta = 0
        self.next_hour = datetime.strptime('2016-01-01 01:00:00',
                                           '%Y-%m-%d %H:%M:%S')

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
                'do_purchase': False, 'cost': 62, 'qty': 2,
                'avg': 64, 'move_value': -124, 'inv_value': -64,
            },
            {  # 7
                'do_purchase': True, 'cost': 64, 'qty': 4,
                'avg': 64, 'move_value': 256, 'inv_value': 192,
            },
            {  # 8
                'do_purchase': False, 'cost': 51, 'qty': 6,
                'avg': 38, 'move_value': -306, 'inv_value': -114,
            },
            {  # 9
                'do_purchase': False, 'cost': 38, 'qty': 2,
                'avg': 38, 'move_value': -76, 'inv_value': -190,
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

    def do_picking(self, picking_ids=False):
        for picking_id in picking_ids:
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

            for move_id in picking_id.move_lines:
                self.delta += 1
                self.next_hour = datetime.strptime(
                    '2016-01-01 01:00:00',
                    '%Y-%m-%d %H:%M:%S') + timedelta(hours=self.delta)
                move_id.write({'date': self.next_hour})

    def create_purchase_order(self, qty=False, cost=False):
        purchase_order_id = self.purchase_order.create({
            'partner_id': self.partner_id.id,
            'location_id': self.ref('stock.stock_location_stock'),
            'pricelist_id': self.ref('purchase.list0'),
            'order_line': [(0, 0, {
                'name': "%s (qty=%s, cost=%s)" % (
                    self.product_id.name, qty, cost),
                'product_id': self.product_id.id,
                'price_unit': cost,
                'product_qty': qty,
                'date_planned': datetime.now().strftime('%Y-%m-%d'),
            })]
        })

        purchase_order_id.wkf_confirm_order()
        purchase_order_id.action_invoice_create()
        purchase_order_id.action_picking_create()
        self.do_picking(purchase_order_id.picking_ids)

    def create_sale_order(self, qty=False, price=False):
        sale_order_id = self.sale_order.create({
            'partner_id': self.partner_id.id,
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
        self.do_picking(sale_order_id.picking_ids)
        return sale_order_id

    def get_stock_valuations(self):
        return self.sc_product._stock_card_move_get(self.product_id.id)['res']

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

        card_lines = self.get_stock_valuations()

        df = pd.DataFrame(card_lines)
        tbl_sc = tabulate(df, headers='keys', tablefmt='psql')
        _logger.info('Gotten Stock Card \n%s', tbl_sc)

        df = pd.DataFrame(self.inv_ids)
        tbl_sc = tabulate(df, headers='keys', tablefmt='psql')
        _logger.info('Expected Stock Card \n%s', tbl_sc)

        self.assertEqual(len(self.inv_ids), len(card_lines),
                         "Both lists should have the same length(=12)")
        for expected, succeded in zip(self.inv_ids, card_lines):
            self.assertEqual(expected['avg'],
                             succeded['average'],
                             "Average Cost %s is not the expected" % expected)

            self.assertEqual(expected['cost'],
                             succeded['cost_unit'],
                             "Unit Cost %s is not the expected" % expected)

            self.assertEqual(expected['inv_value'],
                             succeded['inventory_valuation'],
                             "Inventory Value %s does not match" % expected)

            self.assertEqual(expected['move_value'],
                             succeded['move_valuation'],
                             "Movement Value %s does not match" % expected)
