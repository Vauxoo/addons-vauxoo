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
    "name": "MRP JIT extended",
    "version": "1.0",
    "author" : "Vauxoo",
    "category": "Generic Modules",
    "website" : "http://www.vauxoo.com/",
    "description": """This module uses a wizard to merge an run the procurements
    of the selected manufacturing orders (creating new manufacturing orders) to make a recursive supply
    of the parent orders.
    To apply patches needed use the command:
    patch -b "procurement/procurement.py" "procurement.py.patch"
    patch -b "mrp/mrp.py" "mrp.py.patch"
    """,
    'depends': ['procurement_order_merge', 'mrp_subproduction', 'procurement_location'],
    'init_xml': [],
    'update_xml': [
    'wizard/mrp_jit_extended_wizard_view.xml'
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,

}
