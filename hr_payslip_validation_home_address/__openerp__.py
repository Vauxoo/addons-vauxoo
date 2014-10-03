# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: vauxoo consultores (info@vauxoo.com)
#
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
#

{
    "name": "Hr Payroll Home Address Validation",
    "version": "1.0",
    "author": "Vauxoo",
    "category": "Localization/Mexico",
    "description" : """
    This module adds validation for the field home_address of the employee in payroll
    Just have to install the module, not to do any configuration.
    This field home_address is found in form view HR / Payroll Employee / Employee_id
    in "Personal Information" tab If the field home_address is empty you can not confirm
    that employee's payroll and will see the message that the employee needs to have a
    home address, otherwise if may confirm the payroll.
    """,
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "hr_payroll",
        "hr_payroll_account"
    ],
    "data": [
    ],
    "test": [],
    "installable": True,
    "active": False,
}
