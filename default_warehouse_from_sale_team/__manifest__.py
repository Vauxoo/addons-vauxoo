# coding: utf-8
{
    'name': "Sale Team Warehouse",
    'summary': """Adding a field for the default user warehouse and modifying
    the global default method for assign in any related field the correct
    default warehouse.
    """,
    'author': "Vauxoo",
    'website': "http://www.vauxoo.com",
    'license': 'AGPL-3',
    'category': '',
    'version': '10.0.2.0.0',
    'depends': [
        'sale_stock',
        #  TODO: Remove "delivery" if the following issue is fixed
        #  https://github.com/odoo/odoo/pull/13458
        'delivery',
        'sales_team',
        'base_action_rule',
        'purchase_requisition',
    ],
    'test': [
    ],
    'data': [
        'views/sales_team_view.xml',
        'views/res_users_view.xml',
        'views/stock_view.xml',
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'security/ir_rule.xml',
        'data/ir_actions_server.xml',
        'data/base_action_rule.xml',
    ],
    'demo': [
        # 'demo/stock_demo.xml',
    ],
}
