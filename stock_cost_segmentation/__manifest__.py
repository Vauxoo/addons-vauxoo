# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Stock Cost Segmentation',
    'summary': '''
    ''',
    'version': '12.0.1.0.0',
    'author': 'Vauxoo',
    'category': 'Accounting',
    'license': 'OEEL-1',
    'depends': [
        'stock_account',
        'l10n_mx_edi_landing',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_actions_server.xml',
        'views/product_historical_view.xml',
        'views/product_views.xml',
        'views/stock_location_view.xml',
        'views/stock_move_costs.xml',
    ],
    'demo': [
        'demo/account_minimal_test.xml',
        'demo/stock.xml',
    ],
    'installable': True,
    'post_init_hook': 'pre_init_hook',
}
