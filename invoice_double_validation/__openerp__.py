# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: hugo@vauxoo.com
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################

{
    'name': 'Double validation in account_invoice',
    'version': '8.0.0.1.6',
    'author': 'Vauxoo',
    'license': 'AGPL-3',
    'category': '',
    'depends': [
        'account',
    ],
    'demo': [],
    'website': 'https://www.vauxoo.com',
    'data': [
        'security/two_validations_security.xml',
        'views/two_validations_invoice_view.xml',
    ],
    'test': [],
    "installable": False,
    'auto_install': False,
    'images': [],
}
