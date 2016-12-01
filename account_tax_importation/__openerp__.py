# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Ernesto García Medina (ernesto_gm@vauxoo.com)
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
    "name": "Account tax importation",
    "version": "1.6",
    "author": "Vauxoo",
    "category": "Localization/Mexico",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "account_invoice_tax",
        "account_voucher_tax",
    ],
    "demo": [
        "demo/account_tax_demo.xml",
        "demo/product_broker_demo.xml",
        "demo/partner_broker.xml",
    ],
    "data": [
        "data/account_tax_category_data.xml",
        "view/res_partner_view.xml",
        "view/account_invoice_view.xml"],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": False,
    "auto_install": False,
}
