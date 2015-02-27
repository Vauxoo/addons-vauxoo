#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Humberto Arocha / Nhomar Hernandez
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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
{
    "name": "Account Smart Unreconcile",
    "version": "1.0",
    "author": "Vauxoo",
    "category": "Generic Modules/Accounting",
    "description": """
        Allows send and account_move_reconcile and
        a list of aml_ids to be excluded from reconciliation,
        so that the result is a new account_move_reconcile
        without aml_ids.

        In Future this module is intended to grow adding a wizard
        that would allow an end user to do smart unreconciliations

    """,
    "website": "http://vauxoo.com",
    "license": "",
    "depends": [
        "account",
        "account_reconcile_grouping",
    ],
    "demo": [],
    "data": [],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "active": False
}
