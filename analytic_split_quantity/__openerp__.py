#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
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
    "name": "Analytic Entry Line Split Unit Amount", 
    "version": "1.0", 
    "author": "Vauxoo", 
    "category": "", 
    "description": """
Analytic Entry Line Split Unit Amount
-------------------------------------
This module adds a new field named split_unit_amount which will accordingly
spread the values in the analytic entry lines the amount which was set in the
Journal Entry Line 

The following example illustrated the use of this module.

Hey, Pancho, Sell 10 Barrels of Oil, each one costs 100 USD, Give each of your
boys (4 boys) 60% Iraq, 30% Venezuela, 20%Saudi Arabia and 10%Kuwait,

What you are expected to have in your reports is

600 USD, 6 Barrels, Iraq
300 USD, 3 Barrels, Venezuela
200 USD, 2 Barrels, Saudi Arabia
100 USD, 1 Barrels, Kuwait

This is what is reported without this module 

600 USD, 10 Barrels, Iraq
300 USD, 10 Barrels, Venezuela
200 USD, 10 Barrels, Saudi Arabia
100 USD, 10 Barrels, Kuwait

""", 
    "website": "http://www.vauxoo.com/", 
    "license": "", 
    "depends": [
        "account", 
        "analytic", 
        "account_analytic_plans"
    ], 
    "demo": [], 
    "data": [
        "view/account_analytic_plans_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: