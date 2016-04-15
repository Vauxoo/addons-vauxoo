# coding: utf-8
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Luis Torres (luis_t@vauxoo.com)
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
    "name": "HR Employee Last Name",
    "version": "9.0.0.1.6",
    "author": "Vauxoo",
    "category": "hr",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "hr",
    ],
    "test": [
        "test/test_employee.yml",
    ],
    "demo": [
        "demo/hr_employee.xml",
    ],
    "data": [
        "view/hr_employee_view.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
