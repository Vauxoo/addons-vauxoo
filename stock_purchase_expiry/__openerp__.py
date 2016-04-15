# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
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
    'name': 'Stock Purchase Expiry',
    'version': '9.0.0.1.6',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com/',
    'license': 'AGPL-3',
    'category': '',
    'depends': [
        'purchase',
        'stock',
    ],
    'data': [
        'view/purchase_order_view.xml',
        'view/stock_picking_view.xml',
        'wizard/stock_invoice_onshipping_view.xml',
    ],
    'demo': [],
    'test': [],
    'qweb': [],
    'js': [],
    'css': [],
    'installable': False,
}
