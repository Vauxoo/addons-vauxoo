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
    "name": "PR Line related PO Line", 
    "version": "1.0", 
    "author": "Vauxoo", 
    "category": "", 
    "description": """
Add purchase_requisition_line_id field, it is id of purchase requisition line from where purchase
order line is created, overwrite  the make_purchase_order method for add value of
purchase_requisition_line_id to record purchase order line, it is help to make best inherit and
modification of make_purchase_order method, as can be seen in
purchase_requisition_line_description, purchase_requisition_line_analytic and
purchase_requisition_requisitor modules.
''',
    'depends': [
        'purchase',
        'purchase_requisition',
        ],
    'data': [],
    'demo': [],
    'test': [],
    'qweb': [],
    'js': [],
    'css': [],
    'active': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: