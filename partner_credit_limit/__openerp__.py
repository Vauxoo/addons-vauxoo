# -*- coding: utf-8 -*-
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
    "name": "Partner Credit Limit",
    "version": "1.0",
    "author": "Vauxoo",
    "category": "",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "account",
        "sale",
        "payment_term_type", ],
    "demo": [],
    "data": [
        "view/invoice_workflow.xml",
        "view/sale_order_view.xml",
        "view/partner_view.xml",
    ],
    "installable": True,
}
