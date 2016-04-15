# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Vauxoo
#    Author : Osval Reyes <osval@vauxoo.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': 'CRM Claim Summary Report',
    'category': 'Customer Relationship Management',
    'author': 'Vauxoo, Odoo Community Association (OCA),',
    'website': 'www.vauxoo.com',
    'license': 'AGPL-3',
    'version': '9.0.1.0.0',
    'depends': [
        'crm_claim_rma',
        'report',
    ],
    'demo': [
        'demo/res_company.xml',
    ],
    'data': [
        'views/res_company.xml',
        'reports/claim_summary_report_layouts.xml',
        'reports/claim_summary_report.xml',
    ],
    'installable': True,
    'auto_install': False,
}
