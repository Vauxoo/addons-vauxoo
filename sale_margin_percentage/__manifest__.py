# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Sale Order Gross Margin Percentage",
    "version": "12.0.1.0.0",
    "author": "Vauxoo",
    "category": "",
    "website": "http://www.vauxoo.com/",
    "license": "LGPL-3",
    "depends": [
        "sale_margin",
    ],
    "demo": [],
    "data": [
        'security/sale_margin_percentage_security.xml',
        "views/sale_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
