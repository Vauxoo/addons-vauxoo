# Copyright 2021 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    'name': 'Account Bank Reconcile Transfer',
    'summary': '''Create bank transfers directly from the bank reconciliation screen.''',
    'author': 'Vauxoo',
    'website': 'https://www.vauxoo.com',
    'license': 'AGPL-3',
    'category': 'Installer',
    'version': '13.0.1.0.0',
    'depends': [
        'account',
    ],
    'data': [
        'views/assets.xml',
    ],
    'demo': [],
    'qweb': [
        'static/src/xml/bank_reconciliation.xml',
    ],
    'external_dependencies': {},
    'installable': True,
    'auto_install': False,
    'application': False,
}
