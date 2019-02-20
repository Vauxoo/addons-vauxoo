# coding: utf-8
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Luis Torres (luis_t@vauxoo.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from openerp.tests import common
import time
from openerp import workflow


class TestTaxCommon(common.TransactionCase):

    def setUp(self):
        super(TestTaxCommon, self).setUp()

        self.purchase_obj = self.env['purchase.order']
        self.purchase_line_obj = self.env['purchase.order.line']
        self.currency_rate_obj = self.env['res.currency.rate']

        self.purchase_demo = self.env.ref('purchase.purchase_order_1')
        self.uid = self.ref('base.user_demo')
        self.user_root = self.ref('base.user_root')
        self.product_demo = self.env.ref('product.product_product_1')
        self.currency_usd = self.env.ref('base.USD')
        self.company_id = self.env.ref('base.main_company')

        self.currency_rate_obj.create({
            'name': time.strftime('%Y-%m-%d'),
            'currency_id': self.currency_usd.id,
            'rate': 0.1
        })

        self.currency_rate_obj.create({
            'name': time.strftime('%Y-%m-%d'),
            'currency_id': self.company_id.currency_id.id,
            'rate': 1.0
        })

        # I configure limit_amount and limit_amount_t in wizard of purchase
        self.env['purchase.config.settings'].create({
            'limit_amount': 2000,
            'limit_amount_t': 100000,
        }).execute()

        # I change demo user as purchase manager
        self.env.ref('purchase.group_purchase_manager').write(
            {'users': [(4, self.uid, 0)]})

    def generate_confirm_po(self, amount, currency_id=False):
        purchase = self.purchase_demo.copy()
        if currency_id:
            purchase.write({'currency_id': currency_id})
        purchase.order_line.unlink()
        self.purchase_line_obj.create({
            'product_id': self.product_demo.id,
            'name': 'Product demo',
            'product_qty': 1,
            'date_planned': time.strftime('%Y/%m/%d'),
            'price_unit': amount,
            'order_id': purchase.id
        })
        self.assertEquals(
            purchase.state, 'draft', 'No order in draft')
        self.assertRaises(workflow.trg_validate(
            self.uid, 'purchase.order', purchase.id, 'purchase_confirm',
            self.cr))
        return purchase
