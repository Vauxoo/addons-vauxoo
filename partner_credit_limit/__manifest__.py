# Copyright 2019 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Partner Credit Limit",
    "version": "12.0.1.0.2",
    "author": "Vauxoo",
    "category": "",
    "website": "http://www.vauxoo.com/",
    "license": "LGPL-3",
    "depends": [
        "account",
        "sale",
        "payment_term_type", ],
    "demo": [
    ],
    "data": [
        "views/partner_view.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
