#!/usr/bin/python
# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
#
#    Coded by: Jorge Angel Naranjo Rogel (jorge_nr@vauxoo.com)
#
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
#
{
    "name": "Electronic Invoicing Settings",
    "version": "1.0",
    "depends": [
        'base',
        'account',
        'email_template',
        'email_template_multicompany',
        'report_multicompany'
    ],
    "author": "Vauxoo",
    "description" : """
Electronic Invoicing Settings
=============================

This module helps to configure the electronic invoicing CFD, CBB and CFDI,
with this module you can configure the email template and report template
for electronic invoicing, also your outgoing mail server by company.

    """,
    "website": "http://vauxoo.com",
    "category": "Addons Vauxoo",
    "demo": [],
    "test": [],
    "data": [
        'view/res_config_view.xml',
    ],
    'application': True,
    "active": False,
    "installable": True,
}
