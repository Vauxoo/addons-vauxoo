# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    code by rod@vauxoo.com
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
    'name' : "Account Analytic Account Rent",
    'category' : "account_analytic",
    'version' : "1.0",
    'depends' : ['account_analytic_analysis','product','account_voucher'],
    'author' : "Vauxoo",
    'description' : """
        This module added product in account_analytic_analysis to product control
        """,
    'data' : ['account_analytic_account_rent.xml',
        'product_view.xml',
        'account_analytic_analysis_report.xml',
        'wizard/lines_invoice_create_view.xml',
        'res_company_view.xml'],
    'installable': True,
    'auto_install': False,
}
