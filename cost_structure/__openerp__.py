#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.
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
    "name": "Cost Structure", 
    "version": "0.1", 
    "author": "Vauxoo", 
    "category": "Generic Modules", 
    "description": """
    Module that performs a calculation of average cost in products,
    this module performs a search of all movements made by you for goods
    and are assigned to cost structure.
    This module creates a new tab in the product view, where we have the cost structure for product and price list.
    The average cost is calculated automatically when validating an invoice or credit note, the price list is created
    by a wizard located in the sales configuration menu.
    The product has a list price, the sale must respect the price structure proposed by the calculation, since you will
    not be allowed the confirmation of an operation if any of the suggested prices is not in accordance with the established ragos product price list.
    In the menu of sale may select which type of price you want to sell the product





    """, 
    "website": "http://vauxoo.com", 
    "license": "", 
    "depends": [
        "account", 
        "stock", 
        "product", 
        "purchase", 
        "invoice_date_time"
    ], 
    "demo": [], 
    "data": [
        "data/data_load.xml", 
        "security/cost_structure_security.xml", 
        "security/ir.model.access.csv", 
        "wizard/update_price_list_view.xml", 
        "view/cost_structure.xml", 
        "view/product_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}