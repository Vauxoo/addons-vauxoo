# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Yennifer Santiago <yennifer@vauxoo.com>
#    planned by: Julio Serna <julio@vauxoo.com>
############################################################################
{
    'name': "Stock Propagation Transfer",
    'license': "LGPL-3",
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com/',
    'category': '',
    'version': '8.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'stock',
    ],

    # always loaded
    'data': [
        'views/procurement_rule_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}
