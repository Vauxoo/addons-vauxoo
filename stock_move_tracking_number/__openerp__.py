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
    "name": "Stock Move Tacking Number",
    "summary": "Add tracking number to the moves",
    "license": "LGPL-3",
    "version": "8.0.1.0.0",
    "author": "Vauxoo",
    "website": "http://www.vauxoo.com/",
    "category": "Stock",
    "depends": [
        "stock"
    ],
    "data": [
        "wizards/modify_tracking_number_views.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
    ],
    "demo": [],
    "test": [],
    "qweb": [],
    "installable": False,
}
