#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
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

{
    'name': 'POS Product Filter',
    'version': '1.0',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com/',
    'category': 'Point Of Sale',
    'description': '''
POS Product Filter
==================

This module adds two fields (delivery and restaurant) to the product model, each field is a boolean
and determine if the product will show in delivery and/or restaurant point of sale. The products
view depends of the deli_rest field of the point of sale configuration which can be a restaurant or
delivery.
    ''',
    'depends': ['base', 'point_of_sale', 'sale', 'pos_delivery_restaurant'],
    'data': [
            'view/product_view.xml', 
        ],
    'demo': [],
    'test': [],
    'js': [
        'static/src/js/backbone-super-min.js',
        'static/src/js/db.js',
        'static/src/js/models.js',
        'static/src/js/widgets.js',
        'static/src/js/main.js', 
        ],
    'active': False,
    'installable': True,
}
