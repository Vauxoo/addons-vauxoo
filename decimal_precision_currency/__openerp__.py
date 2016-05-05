# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Maria Gabriela Quilarque  <gabriela@openerp.com.ve>
#    Planified by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Audited by: Maria Gabriela Quilarque  <gabriela@openerp.com.ve>
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
# -
{
    "name": "Decimal Precision to Rate Currency",
    "version": "8.0.0.0.6",
    "author": "Vauxoo",
    "category": "Administracion/Personalizacion/Estructura de la base de datos/Precision Decimal",
    "website": "http://vauxoo.com",
    "license": "",
    "depends": [
        "base",
        "decimal_precision"
    ],
    "demo": [],
    "data": [
        "decimal_pre_currency_view.xml",
        "data/decimal_precision_currency.xml"
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
}
