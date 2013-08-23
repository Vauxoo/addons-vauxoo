#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://www.vauxoo.com>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Humberto Arocha <humbertoarocha@gmail.com>
#    Planified by: Moises Lopez <moylop260@gmail.com>
#    Audited by: Nhomar Hernandez <nhomar@gmail.com>
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
    "name": "Accounting Closure Preparation",
    "version": "1.0",
    "author": "Vauxoo C.A",
    "website": "http://vauxoo.com",
    "category": 'Accounting',
    "description": """
Accounting Closure Preparation.
==============================

Let accounting people do a revision of the Chart of account, in order to avoid
undesirable outcomes when closing a fiscalyear, i.e., transferring balance from
a fiscalyear to be closed to another to be open.
""",
    "depends": ['account'],
    "data": [
        'view/views.xml',
        'view/menues_and_actions.xml',
        ],
    "js": [],
    "qweb": [],
    "css": [],
    "demo": [],
    "test": [],
    "installable": True,
    "active": False,
}
