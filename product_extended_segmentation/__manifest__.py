# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Product Extension to track Segmentation Cost",
    'summary': '''
    ''',
    'version': '11.0.1.0.0',
    'author': 'Vauxoo',
    'category': 'Accounting',
    'license': 'OEEL-1',
    'depends': [
        'product_extended',
        'mrp_workcenter_segmentation',
    ],
    'data': [
        'data/ir_cron.xml',
        'views/res_config_settings_views.xml',
        'views/stock_change_standard_price.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
}
