# Copyright 2022 Vauxoo
# License LGPL-3 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Manual Transfer",
    "author": "Vauxoo",
    "summary": """
    Trigger transfers using a specific route, as it were triggered by a reordering rule
    """,
    "website": "https://www.vauxoo.com",
    "license": "LGPL-3",
    "category": "Inventory/Inventory",
    "version": "15.0.1.0.0",
    "depends": [
        "stock",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/stock_location_route_views.xml",
        "views/stock_manual_transfer_views.xml",
    ],
    "demo": [
        "demo/stock_demo.xml",
    ],
    "installable": True,
    "auto_install": False,
}
