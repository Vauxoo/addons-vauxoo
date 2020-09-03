{
    'name': 'MRP Cost Segmentation',
    'summary': '''
    ''',
    'version': '12.0.1.0.0',
    'author': 'Vauxoo',
    'category': 'Accounting',
    'license': 'OEEL-1',
    'depends': [
        'stock_landed_segmentation',
        'mrp_workcenter_account_move',
        #####
    ],
    'data': [
        'views/mrp_view.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
}
