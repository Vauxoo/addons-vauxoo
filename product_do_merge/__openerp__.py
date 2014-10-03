# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Sabrina Romero (sabrina@vauxoo.com)
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

{
    'name' : 'Merge Duplicate Products',
    'version' : '0.1',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com/',
    'category' : 'Generic Modules',
    'description' : """
Merge Products
==============
We can merge duplicates products and set the new id in all documents of
product merged.

We can merge products using like mach parameter these fields:
    * Name
    * Reference

We can select which product will be the main product.

This feature do not change anything if the products to be merged have
operations in different units of measure.

This feature is in the follow path Warehouse/Tools/Duplicate products
also is created an action menu in the product view.
    """,
    'images' : [],
    'depends' : [
        'base',
        'stock',
    ],
    'data': [
        "security/res_groups.xml",
        'wizard/base_product_merge_view.xml',
    ],
    'js': [
    ],
    'qweb' : [
    ],
    'css':[
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
