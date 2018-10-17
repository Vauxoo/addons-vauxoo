# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Stock Landed Costs Segmentation",
    'summary': '''
    ''',
    'version': '11.0.1.0.0',
    'author': 'Vauxoo',
    'category': 'Accounting',
    'license': 'OEEL-1',
    'depends': [
        "stock_cost_segmentation",
        "stock_landed_costs",
    ],
    'data': [
        'views/stock_landed_costs_view.xml',
        "views/account_invoice.xml",
    ],
    'demo': [
        'demo/stock.xml',
    ],
    'installable': True,
}
