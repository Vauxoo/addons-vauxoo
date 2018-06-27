# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: aguzman@vauxoo.com
#    planned by: Sabrina Romero<sabrina@vauxoo.com>
############################################################################
{
    "name": "Purchase Third Validation",
    "version": "11.0.1.0.0",
    "author": "Vauxoo",
    "category": "Customization",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "purchase"
    ],
    "demo": [],
    "data": [
        'security/purchase_third_validation_group.xml',
        'views/purchase_view.xml',
        'views/purchase_third_validation.xml',
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False
}
