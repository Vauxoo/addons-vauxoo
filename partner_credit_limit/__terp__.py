#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Partner Credit Limit',
    'version': '1.0',
    'depends': ["base", "account", "sale"],
    "author": "Tiny",
    "description": """Partner Credit Limit'
    Checks for all over due payment and already paid amount
    if the differance is positive and acceptable then Salesman
    able to confirm SO
    """,
    'website': 'http://www.openerp.com',
    'init_xml': [
    ],
    'update_xml': [
        'partner_view.xml',
        'sale_workflow.xml',
        'invoice_workflow.xml',
    ],
    'demo_xml': [

    ],
    'installable': True,
    'active': False,
}
