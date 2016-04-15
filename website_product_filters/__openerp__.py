# coding: utf-8
{
    "name": "Website Product Filters",
    "version": "9.0.0.1.0",
    "author": "Vauxoo",
    "category": "Website",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "website_sale",
        "website_product_brand",
        "website_rate_product",
        "website_sale_options",
    ],
    "demo": [
        'demo/filters_demo_data.xml',
    ],
    "data": [
        'data/filters_data.yml',
        'data/price_ranges_data.xml',
        'data/website_settings_data.xml',
        'security/price_ranges_security.xml',
        'security/ir.model.access.csv',
        'views/product_price_ranges_view.xml',
        'views/assets.xml',
        'views/templates.xml',
        'views/res_config.xml',
    ],
    "test": [],
    "qweb": [
    ],
    "installable": True,
    "auto_install": False,
}
