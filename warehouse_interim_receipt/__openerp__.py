# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Katherine Zaoral <kathy@vauxoo.com>
#    planned by: Rafael Silva <rsilvam@vauxoo.com>
############################################################################

{
    "name": "Warehouse Interim Receipt",
    "summary": "Manage Interim receipt number",
    "version": "8.0.1.0.0",
    "license": "LGPL-3",
    "author": "Vauxoo",
    "website": "http://www.vauxoo.com/",
    "category": "Warehouse",
    "depends": [
        "stock_move_tracking_number",
        "purchase",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/modify_warehouse_receipt_views.xml",
        "wizards/warehouse_receipt_input_view.xml",
        "views/warehouse_receipt.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
        "views/res_config_views.xml",
    ],
    "demo": [
        "demo/stock_move.yml",
    ],
    "test": [],
    "qweb": [],
    "installable": True,
}
