{
    "name": "Stock by Warehouse on MRP_BoM",
    "version": "15.0.1.0.0",
    "summary": """
    Know the stock in all your warehouses with a simple click
    from the mrp bill of material's line form.
    """,
    "author": "Vauxoo",
    "category": "stock",
    "website": "http://www.vauxoo.com/",
    "license": "LGPL-3",
    "depends": [
        "mrp",
        "stock_by_warehouse",
    ],
    "data": [
        'views/mrp_bom_line_views.xml',
        'views/mrp_bom_views.xml'
    ],
    "demo": [
    ],
    "installable": True,
    "auto_install": False,
}
