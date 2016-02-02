# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2016 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Luis Torres <luis_t@vauxoo.com>
############################################################################
{
    "name": "Sale Order Date Due",
    "version": "1.0",
    "author": "Vauxoo",
    "category": "Customization",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "sale"
    ],
    "demo": [],
    "data": [
        'data/ir_conf.xml',
        'views/sale_order_view.xml',
        'views/res_config_view.xml',
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False
}
