# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: fernandoL (fernando_ld@vauxoo.com)
############################################################################
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
##############################################################################

{
    "name": "mrp scheduled onchange product",
    "version": "1.0",
    "author" : "Vauxoo",
    "category": "Generic Modules/Production",
    "website" : "http://www.vauxoo.com/",
    "description": """When you add a product, it sets automatically the default uom
    for the product and the name of the product. Adds too a domain to the field
    product_uom to only show the uom matching the selected product.
    """,
    'depends': ['mrp'],
    'init_xml': [],
    'update_xml': [
        'mrp_view.xml',
        ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
