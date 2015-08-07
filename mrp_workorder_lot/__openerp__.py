# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
# ########### Credits #########################################################
#    Coded by: Katherine Zaoral          <kathy@vauxoo.com>
#    Planified by: Katherine Zaoral      <kathy@vauxoo.com>
#    Audited by: Humberto Arocha         <hbto@vauxoo.com>
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
    "name": "MRP Workorder Lot",
    "version": "1.6",
    "author": "Vauxoo",
    "category": "MRP",
    "website": "http://www.vauxoo.com",
    "license": "",
    "depends": [
        "mrp",
        "mrp_operations",
        "mrp_consume_produce",
        "mrp_product_capacity"
    ],
    "demo": [
        "demo/mrp_workorder_lot_demo.xml"
    ],
    "data": [
        "view/mrp_workorder_lot_view.xml",
        "view/res_config_view.xml",
        "view/res_company_view.xml",
        "wizard/mrp_consume_produce.xml",
        "data/mrp_workorder_lot_data.xml",
        "security/ir.model.access.csv"
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "active": False
}
