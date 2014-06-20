#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
################# Credits######################################################
#    Coded by: Luis Escobar <luis@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
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
    "name": "Warranties Enterprise",
    "version": "0.1",
    "depends": [
                "base",
                "account_analytic_analysis",
                "project",
                ],
    "author": "Vauxoo",
    "description": """
Enterprise Contract Management.
===============================

When you are partner sometimes need to be sure manage internally the tickets
and the renewal process of OpenERP Enterprise licences regarding to your
customer contracts this module allow you manage this informatio related to
this contracts.

* Start Date.
* End Date.
* Licence KEy.

#TODO:

* Expiration Warnings.
* Manage Comunication with OpenERP.
    """,
    "website": "http://vauxoo.com",
    "category": "Contracts",
    "demo": [
        'demo/demo_account_analytic_account.xml',
    ],
    "data": [
        'security/ir.model.access.csv',
        'view/account_analytic_analysis_view.xml',
    ],
    "test": [
        'test/contract_enterprise_license.yml'
    ],
    "active": False,
    "installable": True,
}
