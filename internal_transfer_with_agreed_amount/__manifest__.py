{
    'name': 'Internal transfers with an agreed amount',
    'version': '11.0.1.0.0',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com/',
    'license': 'LGPL-3',
    'category': 'account',
    'depends': [
        'account',
    ],
    'data': [
        # Security
        'security/security.xml',
        # Wizards
        'wizards/internal_transfer_multicurrency_view.xml',
        # Views
        'views/account_payment.xml',
    ],
    "installable": True,
}
