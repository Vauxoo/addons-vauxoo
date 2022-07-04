# Copyright 2021 Vauxoo
# License LGPL-3 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': 'Point of Sale Blind Close',
    'summary': '''
    ''',
    'author': 'Vauxoo',
    'website': 'https://www.vauxoo.com',
    'license': 'LGPL-3',
    'category': 'Installer',
    'version': '15.0.1.0.0',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'views/pos_config_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_blind_close/static/src/pos/js/**/*',
        ],
        'web.assets_qweb': [
            'pos_blind_close/static/src/pos/xml/**/*',
        ],
        'web.assets_tests': [
            'pos_blind_close/static/src/pos/tests/tours/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
