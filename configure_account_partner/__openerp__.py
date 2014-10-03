# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Julio Serna (julio@vauxoo.com)
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
    "name": "Configure Account to partners", 
    "version": "0.1", 
    "author": "Vauxoo", 
    "category": "Customization", 
    "description": """
Configure Accounts On imported Partners:
========================================

Background:
-----------

When you import a lot of partners from several sources, It is so common that
all of them are setted with a payable and receiveble account by default, with
this wizard you can fix this quickly one time you upload all partners.

1.- Creates a wizard where you choose an account and write all partners
that are customers and selected on the wizard with this selected account.

2.- Clean the company_id on the property to be able to use the same <head></head>
on all reports.

**TODO:** This feature is so wired, when we fix the correct behaviour this feature
must be removed.

                    """, 
    "website": "http://vauxoo.com", 
    "license": "", 
    "depends": [
        "account", 
        "group_configurations_account"
    ], 
    "demo": [], 
    "data": [
        "wizard/conf_wizard.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: