{
    "name": "Stock by Warehouse",
    "version": "12.0.1.0.0",
    "summary": """
    Know the stock in all your warehouses with a simple click
    from the product form.
    """,
    "author": "Vauxoo",
    "category": "stock",
    "website": "http://www.vauxoo.com/",
    "license": "LGPL-3",
    "depends": [
        "stock",
    ],
    "data": [
        'views/assets.xml',
        'views/product_views.xml',
    ],
    "demo": [
    ],
    'qweb': [
        "static/src/xml/template.xml",
    ],
    "installable": True,
    "auto_install": False,
}
