{
    'name': 'Website Mass Mailing Campaigns',
    'version': '1.0',
    'author': 'Vauxoo, Odoo',
    'category': 'Hidden',
    'depends': [
        'website',
        'mass_mailing'
    ],
    'data': [
        'views/website_mass_mailing.xml',
        'views/unsubscribe.xml',
        'views/snippets.xml',
    ],
    'auto_install': True,
}
