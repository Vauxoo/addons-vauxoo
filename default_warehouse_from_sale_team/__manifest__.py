{
    'name': "Default Warehouse from Sales Team",
    'summary': """Adding a field for the default user warehouse and modifying
    the global default method for assign in any related field the correct
    default warehouse.
    """,
    'author': "Vauxoo",
    'website': "http://www.vauxoo.com",
    'license': 'LGPL-3',
    'category': 'Inventory/Inventory',
    'version': '14.0.1.0.0',
    'depends': [
        'sale_stock',
        'purchase_requisition',
    ],
    'test': [
    ],
    'data': [
        'views/crm_team_views.xml',
        'views/ir_sequence_views.xml',
        'views/res_users_views.xml',
        'views/stock_picking_type_views.xml',
        'security/res_groups.xml',
        'security/ir_rule.xml',
    ],
    'demo': [
        'demo/stock_demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
