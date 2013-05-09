# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
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
    "name": "MRP Consume Produce",
    "version": "1.1",
    "author" : "Vauxoo",
    "category": "Generic Modules/Production",
    "website" : "http://www.vauxoo.com/",
    "description": """ Add wizard to consume and produce.It will be necesary to apply the patch 
        patch/stock.patch, product_py & stock_py located in this module ( useatch -b stock.py  stock.patch )
    """,
    'depends': ['mrp'],
    'init_xml': [],
    'update_xml': [
        'wizard/wizard_view.xml',
        'mrp_consume_produce_view.xml',
        'security/mrp_security.xml',
        'security/ir.model.access.csv',
        ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
 
