# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: hugo@vauxoo.com
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################
{
    "name": "Stock Picking with Invoice Validations",
    "version": "1.0",
    "author": "Vauxoo",
    "category": "",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "sale",
        "stock_account",
        # Conflicts!
        "stock_picking_log_message_transfer",
        "crm_rma_lot_mass_return",
        "yoytec_customer_rma_workflow",
    ],
    "demo": [
        "demo/stock_product_lot_demo.xml",
    ],
    "data": [
        "view/stock_picking_view.xml",
    ],
    "installable": True,
}
