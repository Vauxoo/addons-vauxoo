# coding: utf-8
{
    "name": "Website Extra Variants Options",
    "version": "8.0.0.1.6",
    "author": "Vauxoo",
    "category": "eCommerce",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "website_sale",
        "website_rate_product",  # In to add read reviews link
        "website_product_comment_purchased",  # In to add read reviews link
        "website_product_filters",  # In to add share product icons
    ],
    "demo": [
        "demo/demo.xml",
        "demo/website_settings.yml",
    ],
    "data": [
        "views/layout.xml",
        "views/templates.xml",
        "views/product_printable_view.xml",
        "views/product_report.xml",
        "views/report_layout.xml",
    ],
    "test": [],
    "installable": False,
}
