# -*- coding: utf-8 -*-
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
    'name': 'Register CFDI Information',
    'version': '0.1',
    'category': 'Vauxoo Ondemmand',
    'complexity': 'easy',
    'description': """
Contpaq OpenERP onDemmand Service

The plan for Contpaq Openerp:
========================================

1.- Only visible in the Client Dashboard.
2.- Webserve available to upload the Database.

THe logic is this.

Client Pay (Gain Positive Money Balance) > Client gain access to View to upload
> Client Upload > Server make the magic > Server Send A message "All ready"
    """,
    'author': 'Vauxoo',
    'depends': [
                'account_analytic_analysis', #Each customer will have one and only one Contract one time he pay. 
                'project_issue', #Each contract will have an issue per database. 
                'account', #Necesary to compute balance.
                ],
    'data': [
        'cfdi_register_view.xml',
    ],
    'test': [
        #'test/contact_form.yml',
    ],
    'installable': True,
    'auto_install': False,
    'css': ['static/src/css/style.css', ],
    'js': ['static/src/js/smart.js'],
    'qweb': [], 
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
