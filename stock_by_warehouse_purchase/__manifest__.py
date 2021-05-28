{
    "name": "Stock by Warehouse on Purchases",
    "version": "14.0.1.0.0",
    "summary": """
    Know the stock in all your warehouses with a simple click
    from the purchase order line form.
    """,
    "author": "Vauxoo",
    "category": "stock",
    "website": "http://www.vauxoo.com/",
    "license": "LGPL-3",
    "depends": [
        "stock_by_warehouse",
        "purchase",
    ],
    "data": [
        'views/purchase_view.xml',
    ],
    "demo": [
    ],
    "installable": True,
    "auto_install": False,
}
