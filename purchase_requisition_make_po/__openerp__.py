 ##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    'name': 'Purchase Requisitions Description',
    'version': '0.1',
    'author': 'Vauxoo',
    'category': 'Purchase Management',
    'website': 'http://www.vauxoo.com',
    'description': """
This module allows you to manage your Purchase Requisition.
===========================================================
Add description on product

Technical warning
Add method override to def make_purchase_order from purchase_requisition
""",
    'depends' : ['purchase_requisition'],
    'data': [ 'purchase_requisition_view.xml',
              
            ],
    
    'auto_install': False,
    'installable': True,
}
