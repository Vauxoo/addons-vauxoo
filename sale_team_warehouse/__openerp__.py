# coding: utf-8
{
    'name': "Sale Team Warehouse",
    'summary': """
Adding a field for the default user warehouse and
modifing the global default method for asign in any
realted field the correct default warehuse.
    """,
    # Autoloaded on v8.0 from README.rst
    # 'description': """
    'author': "Vauxoo",
    'website': "http://www.vauxoo.com",
    'license': 'AGPL-3',
    'category': '',
    'version': '9.0.0.0.1',
    'depends': [
        # We must respect the "sequence" now due to demo data in testing
        # process may fail unspectly.
        'base',
        'sale',
        'stock',
        'crm',
        'sales_team',
    ],
    'test': [
    ],
    'data': [
        'views/sales_team_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
