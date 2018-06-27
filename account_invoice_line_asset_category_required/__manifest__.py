# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: jorge_nr@vauxoo.com
#    planned by: Humberto Arocha <hbto@vauxoo.com>
############################################################################
{
    'name': 'Account Invoice Line Asset Category Required',
    'version': '11.0.0.1.6',
    'author': 'Vauxoo',
    'license': 'AGPL-3',
    'category': '',
    'depends': [
        'account',
        'account_asset',
    ],
    'demo': [
        'demo/account_invoice_demo.xml',
    ],
    'website': 'https://www.vauxoo.com',
    'data': [
        'views/account_view.xml'
    ],
    'test': [],
    "installable": True,
    'auto_install': False,
    'images': [],
}
