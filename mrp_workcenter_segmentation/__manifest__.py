# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'MRP Cost Segmentation',
    'summary': '''
    ''',
    'version': '11.0.1.0.0',
    'author': 'Vauxoo',
    'category': 'Accounting',
    'license': 'OEEL-1',
    'depends': [
        'stock_landed_segmentation',
        'mrp_workcenter_account_move',
        #####
    ],
    'data': [
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
}
