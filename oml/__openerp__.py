# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    OML : Openerp Mexican Localization
#    Copyleft (Cl) 2008-2021 Vauxoo, C.A. (<http://vauxoo.com>)
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
{   "name" : "OpenERP Mexican Localization",
    "version" : "",
    "depends" : [
                "city",
                "email_template_multicompany",
                "l10n_mx_account_invoice_tax",
                "l10n_mx_account_tax_category",
                "l10n_mx_base_vat_split",
                "l10n_mx_cities",
                "l10n_mx_company_cif",
                "l10n_mx_company_multi_address",
                "l10n_mx_diot_report",
                "l10n_mx_facturae",
                "l10n_mx_facturae_cbb",
                "l10n_mx_facturae_cer",
                "l10n_mx_facturae_groups",
                "l10n_mx_facturae_group_show_wizards",
                "l10n_mx_facturae_lib",
                "l10n_mx_facturae_pac",
                "l10n_mx_facturae_pac_sf",
                "l10n_mx_facturae_report",
                "l10n_mx_facturae_seq",
                "l10n_mx_import_info",
                "l10n_mx_invoice_amount_to_text",
                "l10n_mx_invoice_currency_chgdft",
                "l10n_mx_invoice_datetime",
                "l10n_mx_invoice_ftp",
                "l10n_mx_invoice_wkf_security",
                "l10n_mx_ir_attachment_facturae",
                "l10n_mx_notes_invoice",
                "l10n_mx_params_pac",
                "l10n_mx_partner_address",
                "l10n_mx_payment_method",
                "l10n_mx_purchase_payment_method",
                "l10n_mx_regimen_fiscal",
                "l10n_mx_res_partner_bank",
                "l10n_mx_sale_payment_method",
                "l10n_mx_settings_facturae",
                "l10n_mx_states",
                "l10n_mx_upload_ftp",
                "account_invoice_line_currency",
                "account_invoice_tax",
                "account_move_line_base_tax",
                "account_move_report",
                "account_voucher_tax",
                "hr_expense_analytic",
                "hr_expense_replenishment",
                "hr_expense_replenishment_tax",
                "report_multicompany",
                ],
    "author" : "Vauxoo",
    "description" : """
Install all apps needed to comply with Mexican laws
===================================================

This module will install for you:
  
  -  city
  
  -  email_template_multicompany
  
  -  l10n_mx_account_invoice_tax
  
  -  l10n_mx_account_tax_category
  
  -  l10n_mx_base_vat_split
  
  -  l10n_mx_cities
  
  -  l10n_mx_company_cif
  
  -  l10n_mx_company_multi_address
  
  -  l10n_mx_diot_report
  
  -  l10n_mx_facturae
  
  -  l10n_mx_facturae_cbb
  
  -  l10n_mx_facturae_cer
  
  -  l10n_mx_facturae_groups
  
  -  l10n_mx_facturae_group_show_wizards
  
  -  l10n_mx_facturae_lib
  
  -  l10n_mx_facturae_pac
  
  -  l10n_mx_facturae_pac_sf
  
  -  l10n_mx_facturae_report
  
  -  l10n_mx_facturae_seq
  
  -  l10n_mx_import_info
  
  -  l10n_mx_invoice_amount_to_text
  
  -  l10n_mx_invoice_currency_chgdft
  
  -  l10n_mx_invoice_datetime
  
  -  l10n_mx_invoice_ftp
  
  -  l10n_mx_invoice_wkf_security
  
  -  l10n_mx_ir_attachment_facturae
  
  -  l10n_mx_notes_invoice
  
  -  l10n_mx_params_pac
  
  -  l10n_mx_partner_address
  
  -  l10n_mx_payment_method
  
  -  l10n_mx_purchase_payment_method
  
  -  l10n_mx_regimen_fiscal
  
  -  l10n_mx_res_partner_bank
  
  -  l10n_mx_sale_payment_method
  
  -  l10n_mx_settings_facturae
  
  -  l10n_mx_states
  
  -  l10n_mx_upload_ftp

Additionally of lp:addons-vauxoo, will be installed:

  -  account_invoice_line_currency
  
  -  account_invoice_tax
  
  -  account_move_line_base_tax
  
  -  account_voucher_tax
  
  -  hr_expense_analytic
  
  -  hr_expense_replenishment
  
  -  hr_expense_replenishment_tax
  
  -  report_multicompany
                    """,
    "website" : "http://www.vauxoo.com",
    "category" : "Localization/Application",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [],
    "test" : [],
    "images" : [],
    "auto_install": False,
    "application": True,
    "installable": True,
}
