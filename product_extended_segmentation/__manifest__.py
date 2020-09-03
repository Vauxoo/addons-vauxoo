{
    "name": "Product Extension to track Segmentation Cost",
    'summary': '''
    ''',
    'version': '12.0.1.0.0',
    'author': 'Vauxoo',
    'category': 'Accounting',
    'license': 'OEEL-1',
    'depends': [
        'mrp_bom_cost',
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
