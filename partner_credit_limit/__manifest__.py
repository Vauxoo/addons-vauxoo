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
    "data": [
        "views/partner_view.xml",
    ],
    "demo": [
        "demo/res_partner_demo.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
