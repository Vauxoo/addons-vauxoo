#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Luis Ernesto García (ernesto_gm@vauxoo.com)
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
    "name" : "Show invoice by user",
    "version" : "1.0",
    "author" : 'Vauxoo',
    "description": """
This module create registration rules for invoice
=================================================

Only lets you see invoice created by the logged user

    """,
    "category" : "Accounting",
    "website" : "http://www.vauxoo.com",
    "depends" : [
        "account"
        ],
    "data" : [
        'security/group_show_invoice.xml',
    ],
    "active": False,
    "installable": True,
}
