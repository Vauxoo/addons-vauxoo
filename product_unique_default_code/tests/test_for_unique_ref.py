# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
###############################################################################
#    Coded by: Sergio Ernesto Tostado Sánchez (sergio@vauxoo.com)
###############################################################################
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
###############################################################################

from openerp.tests.common import TransactionCase
from openerp.exceptions import except_orm


class TestForUniqueRef(TransactionCase):

    """
    This test will prove the new constraint constraint and copy
    ovarriding function to can create a duplicated product with
    a unique internal reference (default_code product field)
    """

    def setUp(self):
        super(TestForUniqueRef, self).setUp()
        self.product_model = self.env['product.product']
        self.product_template_model = self.env['product.template']

    def test_1_copied_product_unique_default_code(self):
        """
        Test 1: This test will prove the next case:
        - Create a product with an internal reference
        - Execute the copy method to create another product record
        - Verify that copied-product has an internal reference totally unique
        """
        product_data = {
            'name': 'Test Cellphone ACME',
            'default_code': '101001000',
            'categ_id': self.env.ref('product.product_category_all').id,
            'standard_price': 100.90,
            'list_price': 123.50
        }
        product = self.product_model.create(product_data)
        self.assertTrue(
            product.copy().default_code != product.default_code,
            "ERROR: New product has not a unique internal reference ..."
        )
