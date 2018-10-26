# Copyright 2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Split Invoices',
    'summary': 'Split invoices to pay them by percentages of the total amount',
    'author': 'Vauxoo',
    'website': 'https://www.vauxoo.com',
    'license': 'AGPL-3',
    'category': 'Accounting',
    'version': '12.0.1.0.0',
    'depends': [
        'account',
    ],
    'data': [
        'wizards/invoice_split.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
