# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Humberto Arocha <hbto@vauxoo.com>
############################################################################
{
    'name': "Stock Account Unfuck",
    'version': '8.0.0.1.0',
    'license': 'LGPL-3',
    'category': '',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com/',
    # any module necessary for this one to work correctly
    'depends': [
        'purchase',
        'stock_account',
    ],
    # always loaded
    'data': [
        'views/view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
}
