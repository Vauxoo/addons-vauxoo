# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Vauxoo, C.A. (<http://vauxoo.com>). All Rights Reserved
#    $Id$
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
{
    "name": "Commercial Chart Account for Venezuela", 
    "version": "1.6", 
    "author": "Tiny & Vauxoo", 
    "category": "Localisation/Account Charts", 
    "website": "", 
    "license": "", 
    "depends": [
        "account", 
        "account_chart"
    ], 
    "demo": [], 
    "data": [
        "account_tax_code.xml", 
        "account_user_types.xml", 
        "charts/account_chart_amd_computer.xml", 
        "charts/account_chart_activa.xml", 
        "charts/account_chart_m321.xml", 
        "account_account.xml", 
        "account_tax_activa.xml", 
        "account_tax_amd.xml", 
        "account_tax_m321.xml", 
        "l10n_chart_ve_wizard.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}