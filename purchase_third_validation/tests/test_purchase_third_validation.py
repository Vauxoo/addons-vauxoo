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
import logging
_logger = logging.getLogger(__name__)
from openerp import workflow


class TestPurchaseThirdValidation(TestTaxCommon):

    def setUp(self):
        super(TestPurchaseThirdValidation, self).setUp()

    def test_purchase_less_2000(self):
        '''
            Test with the amount of purchase order by a total less that minimum
            required to not need a second validation.
        '''
        _logger.info("I test with a total less that 2000")
        purchase = self.generate_confirm_po(100)
        _logger.info("I check that the state of order now is approved")
        state = self.purchase_obj.browse(purchase.id).state
        self.assertEquals(
            state, 'approved', 'No order approved')

    def test_purchase_by_5000(self):
        '''
            Test with the amount of purchase order by a total higher that
            minimum required to need a second validation, but not need a third.
        '''
        _logger.info("I test with a total equal to 5000")
        purchase = self.generate_confirm_po(2000)
        _logger.info("I check the state of order is confirmed")
        state = self.purchase_obj.browse(purchase.id).state
        self.assertEquals(
            state, 'confirmed', 'The order state is not confirmed')
        _logger.info("I try approve the purchase order")
        self.assertRaises(workflow.trg_validate(
            self.uid, 'purchase.order', purchase.id, 'purchase_approve',
            self.cr))
        _logger.info("I check that the state of order now is approved")
        state = self.purchase_obj.browse(purchase.id).state
        self.assertEquals(
            state, 'approved', 'No order approved')

    def test_purchase_by_100000(self):
        '''
            Test with the amount of purchase order by a total higher that
            minimum required to need a third validation.
        '''
        _logger.info("I test with total equal to 100000")
        purchase = self.generate_confirm_po(100000)
        _logger.info("I check the state of order is confirmed")
        state = self.purchase_obj.browse(purchase.id).state
        self.assertEquals(
            state, 'confirmed', 'The order state is not confirmed')
        _logger.info("I try approve the purchase order with demo user")
        self.assertRaises(workflow.trg_validate(
            self.uid, 'purchase.order', purchase.id, 'purchase_approve',
            self.cr))
        _logger.info(
            "I check that the state even is confirmed")
        state = self.purchase_obj.browse(purchase.id).state
        self.assertEquals(
            state, 'confirmed', 'The order was approved')
        _logger.info(
            "I try make the third approbation the purchase order whit root "
            "user")
        self.assertRaises(workflow.trg_validate(
            self.user_root, 'purchase.order', purchase.id, 'purchase_approve',
            self.cr))
        _logger.info(
            "I check that the state of order now is approve")
        state = self.purchase_obj.browse(purchase.id).state
        self.assertEquals(
            state, 'approved', 'No order approved')
