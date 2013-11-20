# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Echeverrifm - http://www.echeverrifm.com.ar
#    All Rights Reserved.
#    info echeverrifm (echeverrifm@gmail.com)
############################################################################
#    Coded by: echeverrifm (echeverrifm@gmail.com)
#    Launchpad Project Manager for Publication: Nhomar Hernandez - nhomar@openerp.com.ve
############################################################################
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
    "name" : "MEXICO - DIOT Report",
    "version" : "1.0",
    "author" : "Federico Manuel Echeverri Choux",
    "category" : "Generic Modules",
    "description": """Module DIOT for  Mexico
    
    The modules 
    - account_move_line_base_tax
    - account_voucher_tax
    are in lp:addons-vauxoo/7.0
    
    If you have old moves without this modules installed, and the company have
    configurated the tax by 'purchase' and by 'sales', you can use the wizard 
    account_update_amount_tax_in_move_lines located in lp:addons-vauxoo/7.0
    to update this moves
    """,
    "website" : "http://www.conectel.mx/",
    "license" : "AGPL-3",
    "depends" : [
        "base_vat",
        "account_move_line_base_tax",
        "account_accountant",
        "l10n_mx_account_invoice_tax",
        "l10n_mx_account_tax_category",
        "l10n_mx_base_vat_split",
        "account_voucher_tax",
        "account_voucher",
        "l10n_mx_partner_address",
        ],
    "demo" : ["demo/account_voucher_tax_demo.xml",
              "demo/res_partner_demo.xml",
              "demo/account_invoice_demo.xml",],
    "data" : [
        "partner_view.xml",
        "wizard/wizard_diot_report_view.xml",
    ],
    'js': [],
    'qweb' : [],
    'css':[],
    'test': ["test/validate_diot.yml",],
    "installable" : True,
    "active" : False,
}
