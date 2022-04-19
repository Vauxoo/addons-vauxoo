# Copyright 2021 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    'name': 'Search Action Domain',
    'summary': 'Send a list of server actions via context to join the domains on the returned actions to a search.',
    'author': 'Vauxoo',
    'website': 'https://www.vauxoo.com',
    'license': 'AGPL-3',
    'category': 'Installer',
    'version': '13.0.1.0.0',
    'depends': [
        'base',
    ],
    'data': [
        'data/ir_actions_server.xml',
    ],
    'demo': [],
    'external_dependencies': {},
    'installable': True,
    'auto_install': False,
    'application': False,
}
