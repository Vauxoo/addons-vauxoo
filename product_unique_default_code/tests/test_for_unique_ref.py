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

from psycopg2 import IntegrityError

from openerp.tests.common import TransactionCase
from openerp.tools.misc import mute_logger


class TestForUniqueRef(TransactionCase):

    """
    This test will prove the new constraint constraint and copy
    ovarriding function to can create a duplicated product with
    a unique internal reference (default_code product field)
    """

    def setUp(self):
        super(TestForUniqueRef, self).setUp()

    @mute_logger('openerp.sql_db')
    def test_constraint_unique_internal_reference(self):
        """
        This test will prove the new constraint added to this module
        to can store only product with unique default_codes (internal refs):
        - Create one new product
        - Duplicate product
        - Set 'default_code' with the same value
        - Check if expected constraint exception is raised
        """
        product_obj = self.env['product.product']
        default_code = '101001000'
        product_data_1 = {
            'name': 'Test Cellphone 1',
            'default_code': default_code,
            'categ_id': self.env.ref('product.product_category_all').id,
            'standard_price': 100.90,
            'list_price': 123.50
        }
        new_product_created = product_obj.create(product_data_1)
        # 'default_code' is set False in duplicated product
        #  Used in copy params "{}" to fix next issue:
        #   https://github.com/odoo/odoo/pull/5236
        product_duplicated = new_product_created.copy({})
        with self.assertRaisesRegexp(
            IntegrityError,
            r'duplicate key value violates unique constraint '
                r'"product_product_default_code_unique"'):
            product_duplicated.write({'default_code': default_code})
