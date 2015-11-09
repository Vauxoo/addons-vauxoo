# coding: utf-8
{
    "name": "Website Product Filters",
    "version": "1.0",
    "author": "Vauxoo",
    "category": "Website",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "website_sale",
        "website_product_brand",
        "website_rate_product",
    ],
    "demo": [],
    "data": [
        'data/price_ranges_data.xml',
        'security/price_ranges_security.xml',
        'security/ir.model.access.csv',
        'views/product_price_ranges_view.xml',
        'views/assets.xml',
        'views/templates.xml',
    ],
    "test": [],
    "qweb": [
    ],
    "installable": True,
    "auto_install": False,
}
