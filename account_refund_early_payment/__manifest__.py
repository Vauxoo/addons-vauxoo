# Copyright 2019 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Account Refund Early Payment',
    'version': '12.0.1.0.0',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com/',
    'license': 'LGPL-3',
    'category': '',
    'depends': [
        'account_accountant',
    ],
    'data': [
        'data/data.xml',
        'wizards/account_invoice_refund_view.xml',
    ],
    'demo': [
    ],
    "installable": True,
}
