#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: javier@vauxoo.com
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
{
    "name": "Stock Card", 
    "version": "0.2", 
    "author": "Vauxoo", 
    "category": "Localization", 
    "description": """
        Kardex.

""", 
    "website": "http://vauxoo.com", 
    "license": "", 
    "depends": [
        "base", 
        "product", 
        "purchase", 
        "account", 
        "stock", 
        "report_profit"
    ], 
    "demo": [], 
    "data": [
        "security/stock_card_security.xml", 
        "security/ir.model.access.csv", 
        "stock_view.xml", 
        "report_profit_picking_view.xml", 
        "stock_card_view.xml", 
        "stock_card_report.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: