# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
#  ############ Credits #######################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Audited by: Jose Morales <jose@vauxoo.com>
###############################################################################

{
    'name': 'Account Refund Early Payment',
    'version': '12.0.0.0.1',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com/',
    'license': 'LGPL-3',
    'category': '',
    'depends': ['account'],
    'data': [
        'data/data.xml',
        'wizards/refund_early_payment.xml',
    ],
    'demo': [
    ],
    'test': [],
    'qweb': [],
    'js': [],
    'css': [],
    "installable": True,
}
