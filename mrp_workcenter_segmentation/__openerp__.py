# coding: utf-8
{
    "name": "MRP Workcenter Segmentation",
    "version": "8.0.1.0.0",
    "author": "Vauxoo",
    "category": "Tools",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "mrp_workcenter_account_move",
        "stock_quant_cost_segmentation",
    ],
    "demo": [
        'demo/demo.xml',
    ],
    "data": [
        'security/ir.model.access.csv',
        'view/view.xml',
        'view/wizard.xml',
    ],
    "installable": True,
    "auto_install": False,
}
