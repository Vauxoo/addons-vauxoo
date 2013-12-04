# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Sabrina Romero (sabrina@vauxoo.com)
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
    "name": "Vauxoo Account Amortization",
    "version": "0.1",
    "depends": [
                "account_asset",
                "account_asset_date",
                "account_asset_analytic",
               ],
    "author": "Vauxoo",
    "licence": "AGPL v3",
    "website": "http://www.vauxoo.com",
    "category": "Accounting & Finance",
    "description": """
Vauxoo Account Amortization.
============================

Work summary:
-------------
- Copy and adapt the view account.asset.asset.form
- Copy the view account.asset.asset.search
- inherit action action_account_asset_asset_form to add domain and default
	the new field its type
	the new values ​​are deprecation and amortization,
	in this case the domain is for type amortization
- Create action for the new form view with domain and default
	in this case the domain is for type deprecation
- The action line call same tree view
- The action line call the new form view
- Menu for call the action

This module adds:
-----------------
- Accounting > Amortization
- Accounting > Amortization > Amortization
- Configuration > Amortization
- Configuration > Amortization > Amortization Categories


See the documentation here:
---------------------------
http://www.principlesofaccounting.com/chapter13/chapter13.html
""",
    "data":[
        "view/account_amortization_view.xml",
        ],
    "installable": True,
    "auto_install": False,
}
