# -*- coding: utf-8 -*-
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
import logging
_logger = logging.getLogger(__name__)
import time
from openerp import workflow


class TestTaxCommon(common.TransactionCase):

    def setUp(self):
        super(TestTaxCommon, self).setUp()

        self.purchase_obj = self.env['purchase.order']
        self.purchase_line_obj = self.env['purchase.order.line']

        self.purchase_demo = self.env.ref('purchase.purchase_order_1')
        self.uid = self.ref('base.user_demo')
        self.user_root = self.ref('base.user_root')
        self.product_demo = self.env.ref('product.product_product_1')

        _logger.info(
            "I configure limit_amount and limit_amount_t in wizard "
            "of purchase")
        self.env['purchase.config.settings'].create({
            'limit_amount': 2000,
            'limit_amount_t': 100000,
        }).execute()

        _logger.info(
            "I change demo user as purchase manager")
        self.env.ref('purchase.group_purchase_manager').write(
            {'users': [(4, self.uid, 0)]})

    def generate_confirm_po(self, amount):
        _logger.info("I duplicate purchase demo")
        purchase = self.purchase_demo.copy()
        purchase.order_line.unlink()
        self.purchase_line_obj.create({
            'product_id': self.product_demo.id,
            'name': 'Product demo',
            'product_qty': 1,
            'date_planned': time.strftime('%Y/%m/%d'),
            'price_unit': amount,
            'order_id': purchase.id
        })
        _logger.info("I check that the initial state of order is draft")
        self.assertEquals(
            purchase.state, 'draft', 'No order in draft')
        _logger.info("I try confirm the purchase order")
        self.assertRaises(workflow.trg_validate(
            self.uid, 'purchase.order', purchase.id, 'purchase_confirm',
            self.cr))
        return purchase
