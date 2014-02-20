# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Jorge Angel Naranjo (jorge_nr@vauxoo.com)
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
    "name": "HR Payroll Mexican",
    "version": "1.0",
    "depends": [
        'hr',
        "hr_payroll",
        'hr_contract',
        'hr_holidays',
        'decimal_precision',
    ],
    "author": "Vauxoo",
    "description": """
HR Payroll Mexican
===================

    """,
    "website": "http://vauxoo.com",
    "category": "Addons Vauxoo",
    "data": ["view/l10n_mx_hr_payroll.xml",
             "view/hr_payslip_inherit.xml",
             "view/hr_contract_inherit.xml",
             "view/hr_payslip_working_day.xml",
             "view/hr_inability_view.xml",
             #~ "data/payroll_category_hext_inability.xml",
             "data/payroll_working_day.xml",
             "data/payroll_inability_data.xml",],
    "test": [],
    "active": False,
    "installable": True,
}
