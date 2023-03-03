{
    "name": "Stock by Warehouse",
    "version": "16.0.1.0.0",
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
        "views/product_product_views.xml",
        "views/product_template_views.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "stock_by_warehouse/static/src/components/warehouse/warehouse_field.scss",
            "stock_by_warehouse/static/src/components/warehouse/warehouse_field.xml",
            "stock_by_warehouse/static/src/components/warehouse/warehouse_field.js",
        ],
    },
    "installable": True,
    "auto_install": False,
}
