# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Luis Torres <luis_t@vauxoo.com>
############################################################################
{
    "name": "Base VAT Country",
    "version": "9.0.0.1.0",
    "author": "Vauxoo",
    "category": "Customization",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "base_vat"
    ],
    "demo": [],
    "data": [
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": False,
    "auto_install": False
}
