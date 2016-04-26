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
    'version': '8.0.0.0.2',
    'depends': [
        'sale_stock',
        'sales_team',
    ],
    'test': [
    ],
    'data': [
        'views/sales_team_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
}
