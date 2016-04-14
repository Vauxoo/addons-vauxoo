# coding: utf-8
{
    'name': "Test Sale Team Warehouse",
    'summary': """
This module test the sales_team_warehouse feature.
    """,
    # Autoloaded on v8.0 from README.rst
    # 'description': """
    'author': "Vauxoo",
    'website': "http://www.vauxoo.com",
    'license': 'AGPL-3',
    'category': '',
    'version': '8.0.0.0.1',
    'depends': [
        # We must respect the "sequence" now due to demo data in testing
        # process may fail unspectly.
        'sale_team_warehouse',
    ],
    'test': [
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
