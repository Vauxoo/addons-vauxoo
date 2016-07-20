# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Luis Escobar                <luis@vauxoo.com>
#              María Gabriela Quilarque    <gabriela@vauxoo.com>
#    Planified by: Nhomar Hernandez        <nhomar@vauxoo.com>
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: María Gabriela Quilarque  <gabriela@vauxoo.com>
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
##########################################################################
###
{
    "name": "CRM Cost Issue",
    "version": "8.0.0.0.6",
    "author": "Vauxoo",
    "category": "Generic Modules/Accounting",
    "website": "http://vauxoo.com",
    "license": "",
    "depends": [
        "base",
        "crm",
        "project",
        "project_issue",
        "product"
    ],
    "demo": [],
    "data": [
        "view/project_task_view.xml"
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
}
