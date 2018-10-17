# -*- coding: utf-8 -*-
# © 2017 Vauxoo, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'author': 'ADHOC SA,Odoo Community Association (OCA), Vauxoo',
    'category': 'Accounting & Finance',
    'depends': ['account'],
    'installable': True,
    'name': 'Account Invoice Change Currency',
    'data': [
        'security/security.xml',
        'wizard/account_change_currency_view.xml',
        'views/invoice_view.xml',
    ],
    'version': '11.0.1.0.0',
    'website': 'www.adhoc.com.ar, www.vauxoo.com',
    'license': 'AGPL-3'
}
