{
    "name": "Stock by Warehouse",
    "version": "15.0.1.0.0",
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
        'views/product_views.xml',
    ],
    "demo": [
    ],
    "assets": {
        "web.assets_backend": [
            "stock_by_warehouse/static/src/js/widget.js",
            "stock_by_warehouse/static/src/scss/main.scss",
        ],
        "web.assets_qweb": [
            "stock_by_warehouse/static/src/xml/template.xml",
        ],
    },
    "installable": True,
    "auto_install": False,
}
