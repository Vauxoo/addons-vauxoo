# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Vauxoo
#    Author : Humberto Arocha <hbto@vauxoo.com>
#             Osval Reyes <osval@vauxoo.com>
#
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
#
##############################################################################
{
    "name": "Product Extension to track Segmentation Cost",
    "version": "8.0.2.0.0",
    "author": "Vauxoo",
    'website': 'https://www.vauxoo.com',
    "license": "AGPL-3",
    "depends": [
        'product',
        'product_extended',
        'mrp_routing_account_journal',
        'stock_card_segmentation',
        'mrp_workcenter_segmentation',
    ],
    "category": "Generic Modules/Inventory Control",
    "demo": [
        "demo/demo.xml",
    ],
    "data": [
        'view/view.xml',
        'view/installer.xml',
        'view/company.xml',
        'data/data.xml',
    ],
    "installable": False
}
