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

from openerp.addons.purchase_third_validation.tests.common import TestTaxCommon
from openerp import workflow


class TestPurchaseThirdValidation(TestTaxCommon):

    def setUp(self):
        super(TestPurchaseThirdValidation, self).setUp()

    def test_purchase_by_1000(self):
        '''Test with the amount of purchase order by a total less that minimum \
        required to not need a second validation, (amount = 1000).
        '''
        purchase = self.generate_confirm_po(1000)
        state = self.purchase_obj.browse(purchase.id).state
        self.assertEquals(state, 'approved', 'No order approved')

    def test_purchase_by_5000(self):
        '''Test with the amount of purchase order by a total higher that \
        minimum required to need a second validation, but not need a third, \
        (amount = 5000).
        '''
        purchase = self.generate_confirm_po(5000)
        state = self.purchase_obj.browse(purchase.id).state
        self.assertEquals(
            state, 'confirmed', 'The order state is not confirmed')
        self.assertRaises(workflow.trg_validate(
            self.uid, 'purchase.order', purchase.id, 'purchase_approve',
            self.cr))
        state = self.purchase_obj.browse(purchase.id).state
        self.assertEquals(
            state, 'approved', 'No order approved')

    def test_purchase_by_100000(self):
        '''Test with the amount of purchase order by a total higher that \
        minimum required to need a third validation, (amount = 100000).
        '''
        purchase = self.generate_confirm_po(100000)
        state = self.purchase_obj.browse(purchase.id).state
        self.assertEquals(
            state, 'confirmed', 'The order state is not confirmed')
        self.assertRaises(workflow.trg_validate(
            self.uid, 'purchase.order', purchase.id, 'purchase_approve',
            self.cr))
        state = self.purchase_obj.browse(purchase.id).state
        self.assertEquals(
            state, 'confirmed', 'The order was approved')
        self.assertRaises(workflow.trg_validate(
            self.user_root, 'purchase.order', purchase.id, 'purchase_approve',
            self.cr))
        state = self.purchase_obj.browse(purchase.id).state
        self.assertEquals(
            state, 'approved', 'No order approved')

    def test_purchase_by_100_usd(self):
        '''Test with the amount of purchase order in USD by a total less that \
        minimum required to not need a second validation (amount = 100 USD).
        '''
        purchase = self.generate_confirm_po(100, self.currency_usd.id)
        state = self.purchase_obj.browse(purchase.id).state
        self.assertEquals(state, 'approved', 'Order in USD no approved')

    def test_purchase_by_5000_usd(self):
        '''Test with the amount of purchase order in USD by a total higher \
        that minimum required to need a second validation, but not need a \
        third, (amount = 500 USD).
        '''
        purchase = self.generate_confirm_po(500, self.currency_usd.id)
        state = self.purchase_obj.browse(purchase.id).state
        self.assertEquals(
            state, 'confirmed', 'The order state in USD is not confirmed')
        self.assertRaises(workflow.trg_validate(
            self.uid, 'purchase.order', purchase.id, 'purchase_approve',
            self.cr))
        state = self.purchase_obj.browse(purchase.id).state
        self.assertEquals(
            state, 'approved', 'Order in USD no approved')

    def test_purchase_by_10000_usd(self):
        '''Test with the amount of purchase order in USD by a total higher \
        that minimum required to need a third validation (amount = 10000 USD).
        '''
        purchase = self.generate_confirm_po(10000, self.currency_usd.id)
        state = self.purchase_obj.browse(purchase.id).state
        self.assertEquals(
            state, 'confirmed', 'The order state is not confirmed')
        self.assertRaises(workflow.trg_validate(
            self.uid, 'purchase.order', purchase.id, 'purchase_approve',
            self.cr))
        state = self.purchase_obj.browse(purchase.id).state
        self.assertEquals(
            state, 'confirmed', 'The order in USD was approved')
        self.assertRaises(workflow.trg_validate(
            self.user_root, 'purchase.order', purchase.id, 'purchase_approve',
            self.cr))
        state = self.purchase_obj.browse(purchase.id).state
        self.assertEquals(
            state, 'approved', 'Order in USD no approved')
