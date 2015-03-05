# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP MEXICO (<http://www.vauxoo.com>).
#    All Rights Reserved
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


class TestProduct(common.TransactionCase):

    def test_create_product(self):
        product_obj = self.env['product.product']
        category_obj = self.env['product.category']
        attributes = [(0, 0, {'name': 'Attr 1'}),
                      (0, 0, {'name': 'Attr 2'}),
                      (0, 0, {'name': 'Attr 3'}), ]
        categ_data = {
            'name': 'Category With Attributes',
            'attribute_ids': attributes,
        }
        categ_id = category_obj.create(categ_data)
        product_data = {
            'name': 'Test Product',
            'categ_id': categ_id.id,
        }
        prod_attr_ids = []
        categ_attr_ids = []
        product_id = product_obj.create(product_data)
        for product in product_id:
            for attribute in product.attribute_line_ids:
                prod_attr_ids.append(attribute.attribute_id.id)
        for categ in categ_id:
            for attribute in categ.attribute_ids:
                categ_attr_ids.append(attribute.id)
        self.assertEqual(categ_attr_ids.sort(), prod_attr_ids.sort())
