{
    "name": "Product Price Cost in USD",
    "summary": """
This module adds the field Cost in USD to the Product form.
    """,
    "version": "15.0.1.0.1",
    "author": "Vauxoo",
    "category": "Sales/Sales",
    "website": "https://vauxoo.com",
    "license": "LGPL-3",
    "depends": [
        "sale_margin",
    ],
    "demo": [
        "demo/product_pricelist_demo.xml",
    ],
    "data": [
        "data/res_currency_data.xml",
        "views/product_template_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
