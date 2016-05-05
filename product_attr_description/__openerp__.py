# coding: utf-8
########################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2011 OpenERP S.A. (<http://www.openerp.com>).
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
#######################################################################
{
    "name": "Product extension to track sales and purchases from variants",
    "version": "8.0.0.1.6",
    "author": "Vauxoo",
    "category": "Technical, Generic Modules/Inventory Control",
    'website': 'https://www.vauxoo.com',
    "license": "AGPL-3",
    "depends": ['product'],
    "data": [
        'view/product_view.xml',
    ],
    "installable": True
}
