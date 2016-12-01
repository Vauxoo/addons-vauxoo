# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Gabriela Quilarque <gabriela@vauxoo.com>
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
    "name": "Stock Transfer Avoid Lot Repeated To Split",
    "summary": "Avoid lot repeated when the item is splited",
    "version": "8.0.1.0.0",
    "author": "Vauxoo",
    "website": "http://www.vauxoo.com/",
    "license": "LGPL-3",
    "category": "stock",
    "depends": [
        "stock",
    ],
    "data": [
        "data/stock_config_settings.xml",
    ],
    "demo": [
        "demo/stock_production_lot.xml",
    ],
    "installable": False,
}
