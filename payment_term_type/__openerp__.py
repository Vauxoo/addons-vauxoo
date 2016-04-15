# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Payment Terms Type',
    'version': '9.0.0.1.0',
    'author': 'Tiny SPRL, Vauxoo',
    'license': 'AGPL-3',
    'category': '',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    "demo": [
        'demo/payment_term_demo.xml',
    ],
    'website': 'https://www.vauxoo.com',
    'data': [
        'views/account_payment_type_view.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
}
