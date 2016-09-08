# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Vauxoo
#    Author : Jose Suniaga <josemiguel@vauxoo.com>
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
from openerp import _
from openerp.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):

    def setUp(self):
        super(TestSaleOrder, self).setUp()
        self.sale_order = self.env['sale.order']
        self.partner_id = self.env.ref('base.res_partner_12').id
        self.product = self.env.ref('product.product_product_6')
        self.pricelist_id = self.env.ref('product.list0').id
        self.sale = self.sale_order.create({
            'partner_id': self.partner_id,
            'order_policy': 'manual',
            'pricelist_id': self.pricelist_id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1.0,
                'price_unit': 100.0,
            })]
        })

    def test_01_qty_available(self):
        res = self.sale.order_line.with_context(show_message='qty_available').\
            product_id_change_with_wh(
                pricelist=self.pricelist_id,
                product=self.product.id,
                partner_id=self.partner_id)
        self.assertIn('warning', res)
        self.assertIn('title', res['warning'])
        self.assertEqual(res['warning']['title'],
                         _('Product available by Warehouse'))

    def test_02_virtual_available(self):
        res = self.sale.order_line.with_context(
            show_message='virtual_available').product_id_change_with_wh(
                pricelist=self.pricelist_id,
                product=self.product.id,
                partner_id=self.partner_id)
        self.assertIn('warning', res)
        self.assertIn('title', res['warning'])
        self.assertEqual(res['warning']['title'],
                         _('Forecast Quantity by Warehouse'))

    def test_03_incoming_qty(self):
        res = self.sale.order_line.with_context(show_message='incoming_qty').\
            product_id_change_with_wh(
                pricelist=self.pricelist_id,
                product=self.product.id,
                partner_id=self.partner_id)
        self.assertIn('warning', res)
        self.assertIn('title', res['warning'])
        self.assertEqual(res['warning']['title'],
                         _('Incoming Quantity by Warehouse'))

    def test_04_outgoing_qty(self):
        res = self.sale.order_line.with_context(show_message='outgoing_qty').\
            product_id_change_with_wh(
                pricelist=self.pricelist_id,
                product=self.product.id,
                partner_id=self.partner_id)
        self.assertIn('warning', res)
        self.assertIn('title', res['warning'])
        self.assertEqual(res['warning']['title'],
                         _('Outgoing Quantity by Warehouse'))
