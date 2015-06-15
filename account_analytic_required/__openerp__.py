# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
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
    "name": "Account Analytic Required",
    "version": "1.0",
    "author": "Vauxoo",
    'category': 'Generic Modules/Accounting',
    "description": """
    This module adds an option "analytic policy" on Account Types.

    You have the choice between 3 policies : always, never and optional. For
    example, if you want to have an analytic account on all your expenses, set
    the policy to "always" for the account type "expense" ; then, if you try to
    save an account move line with an account of type "expense" without
    analytic account, you will get an error message.

    In a preemptively it avoid that an Invoice be validated if using accounts
    that has to fulfil the policy by adding field analytic_required, making
    mandatory filling an Analytic Account when depending on the policy
    selected in the Account Type

    This module uses original code from a module with same name developed by
    Alexis de Lattre <alexis.delattre@akretion.com> during the
    Akretion-Camptocamp code sprint of June 2011. Modification of code has been
    made to comply with Odoo available API.

    """,
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "demo": [

    ],
    "data": [
        "view/account_view.xml",
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "active": False
}
