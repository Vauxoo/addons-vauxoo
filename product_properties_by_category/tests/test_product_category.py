# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Coded by: Hugo Adan <hugo@vauxoo.com>
###############################################################################
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
###############################################################################

from openerp.tests import common


class TestProductCategoryProperties(common.SingleTransactionCase):

    def setUp(self):
        super(TestProductCategoryProperties, self).setUp()
        # Category All / Saleable / Accessories
        self.product_category = self.browse_ref('product.product_category_7')
        # Products / Blank CD
        self.product = self.browse_ref(
            'product.product_product_35_product_template')

    def update_product(self, product):
        res = product.get_purchase_requisition_default()
        product.write({
            'categ_id': product.categ_id.id,
            'purchase_requisition': res,
        })

    def test_01_category_prch_rqst(self):
        """Test 01: Check that the product receive the default value
        defined in the product.category
        """
        # Set "Call for Bids" False to the product.
        self.product.purchase_requisition = False
        # Add a default value "Set True" for "Call for Bids"
        # of product category first in line (Category A).
        self.product_category.purchase_requisition = '1'
        # Simulate the onchange and check that the field
        # in the product change for False to True.
        self.update_product(self.product)
        self.assertTrue(self.product.purchase_requisition)

    def test_02_no_restriction(self):
        """Test 02: No restriction over the inherit values.
        The user can manually change a value inherit form
        the product.category as is needed.
        """
        # Taking the same product in Test 01 change the
        # "Call for Bids" in product to False
        self.product.purchase_requisition = False
        self.assertFalse(self.product.purchase_requisition)
        # Check the new value of product "call for bids" with the
        # product.category A "call for bids" to check that they are different.
        self.assertNotEqual(
            self.product.purchase_requisition,
            bool(int(self.product_category.purchase_requisition)))

    def test_03_sub_category_default_value(self):
        """Test 03: Check pull the default value form
        the parent category one level above.
        """
        category_a = self.product_category
        category_b = category_a.parent_id
        # Remove the default value in Category A
        category_a.purchase_requisition = '-1'
        # Add a default value "Set True" in Category B.
        category_b.purchase_requisition = '1'
        # Set "Call for Bids" False to the product.
        self.product.purchase_requisition = False
        # Simulate the onchane and check that de product "Call for Bids"
        # change to default describe in Category B.
        self.update_product(self.product)
        self.assertTrue(self.product.purchase_requisition)

    def test_04_all_category_default_no_set(self):
        """Test 04: What happen when is not default value
        defined in the product category or in either of its parents.
        """
        # Change the product "Call for Bids" to True.
        self.product.purchase_requisition = True
        self.assertTrue(self.product.purchase_requisition)
        # Remove all default in Category A/B/C. (Set then to "No set").
        category = self.product_category
        while category.parent_id:
            category.purchase_requisition = '-1'
            category = category.parent_id
        # Simulate the onchange and check that the Call for Bids
        # change from True to False.
        self.update_product(self.product)
        self.assertFalse(self.product.purchase_requisition)
