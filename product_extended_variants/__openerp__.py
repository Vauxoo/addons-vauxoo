##############################################################################
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
##############################################################################
{
    "name": "Product extension to track sales and purchases from variants",
    "version": "1.0",
    "author": "Vauxoo",
    'website': 'https://www.vauxoo.com',
    "depends": ['account_anglo_saxon', 'product', 'stock_account',
                'product_extended'],
    "category": "Generic Modules/Inventory Control",
    "description": """
Product extension. This module adds:
  * Computes standard price from the BoM of the product with a button on the
    * product variant based
    on the materials in the BoM and the work centers.  It can create the
    necessary accounting entries when necessary.
""",
    "data": ['view/product_view.xml'],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
