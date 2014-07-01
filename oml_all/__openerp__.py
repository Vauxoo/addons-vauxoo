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
                #Start list of all oficial modules
                "portal_sale",
                "point_of_sale",
                #~ "event_sale",
                #~ "account",Repeated module
                "auth_openid",
                #~ "event", Repeated module
                #~ "l10n_bo",
                #~ "l10n_pe",
                "pad_project",
                "project_mrp",
                "account_accountant",
                #~ "auth_signup",Repeated module
                "event_moodle",
                #~ "l10n_br",
                #~ "l10n_pl",
                #~ "plugin",Repeated module
                "project_timesheet",
                "account_analytic_analysis",
                #~ "base_action_rule",Repeated module
                #~ "l10n_ca",
                #~ "l10n_pt",
                #~ "plugin_outlook",Repeated module
                #~"purchase",Repeated module
                #~ "base_calendar",Repeated module
                #~ "fetchmail",Repeated module
                #~ "l10n_ch",
                #~ "l10n_ro",
                #~ "plugin_thunderbird",Repeated module
                #"purchase_analytic_plans",#Error to fix
                #"account_analytic_plans",#Error to fix
                #~ "base_gengo",Repeated module
                #~ "fleet",Repeated module
                #~ "l10n_cl",
                #~ "l10n_si",
                "account_anglo_saxon",
                #~ "base_iban",Repeated module
                #~ "google_base_account",Repeated module
                #~ "l10n_cn",
                #~ "l10n_syscohada",
                #~ "portal",Repeated module
                "account_asset",
                #~ "base_import",Repeated module
                "google_docs",
                #~ "l10n_co",
                #~ "l10n_th",
                "portal_anonymous",
                "report_intrastat",
                #~ "base_report_designer",Repeated module
                #~ "hr",Repeated module
                #~ "l10n_cr",
                #~ "l10n_tr",
                "portal_claim",
                #~ "report_webkit",Repeated module
                "account_budget",
                #~ "base_setup",Repeated module
                "hr_attendance",
                #~ "l10n_de",
                #~ "l10n_uk",
                "portal_crm",
                "resource",
                "account_cancel",
                #~ "base_status",Repeated module
                "hr_contract",
                #~ "l10n_ec",
                #~ "l10n_us",
                "portal_event",
                #~ "sale",Repeated module
                "account_chart",
                #~ "base_vat",Repeated module
                "hr_evaluation",
                #~ "l10n_es",
                #~ "l10n_uy",
                "portal_hr_employees",
                #"sale_analytic_plans",#Error to fix
                "account_check_writing",
                "board",
                "hr_expense",
                #~ "l10n_et",
                #~ "l10n_ve",
                "portal_project",
                #~ "sale_crm",Repeated module
                "account_followup",
                "claim_from_delivery",
                "hr_holidays",
                #~ "l10n_fr",
                #~ "l10n_vn",
                "portal_project_issue",
                #~ "sale_journal",Repeated module
                "account_payment",
                "contacts",
                "hr_payroll",
                #~ "l10n_fr_hr_payroll",
                #~ "lunch",Repeated module
                "portal_project_long_term",
                #~ "sale_margin",Repeated module
                "account_report_company",
                #~ "crm",
                "hr_payroll_account",
                #~ "l10n_fr_rib",
                #~ "mail",Repeated module
                #~ "sale_mrp",Repeated module
                "account_sequence",
                "crm_claim",
                "hr_recruitment",
                #~ "l10n_gr",
                "marketing",
                "portal_stock",
                #~ "sale_order_dates",Repeated module
                "account_test",
                "crm_helpdesk",
                "hr_timesheet",
                #~ "l10n_gt",
                "marketing_campaign",
                "process",
                #~ "sale_stock",Repeated module
                "account_voucher",
                "crm_partner_assign",
                "hr_timesheet_invoice",
                #~ "l10n_hn",
                "marketing_campaign_crm_demo",
                "procurement",
                #~ "share",Repeated module
                #~ "analytic",Repeated module
                "crm_profiling",
                "hr_timesheet_sheet",
                #~ "l10n_hr",
                "membership",
                #~ "product",Repeated module
                #~ "stock",Repeated module
                "analytic_contract_hr_expense",
                "crm_todo",
                "idea",
                #~ "l10n_in",
                "mrp",
                "product_expiry",
                "stock_invoice_directly",
                "analytic_user_function",
                "decimal_precision",
                "knowledge",
                #~ "l10n_in_hr_payroll",
                "mrp_byproduct",
                "product_manufacturer",
                #"stock_location", #Error to fix
                "anonymization",
                "delivery",
                #~ "l10n_ar",
                #~ "l10n_it",
                "mrp_jit",
                "product_margin",
                "stock_no_autopicking",
                "association",
                #~ "document",
                #~ "l10n_at",
                #~ "l10n_lu",
                "mrp_operations",
                "product_visible_discount",
                "subscription",
                #~ "audittrail",
                #"document_ftp", #No test
                #~ "l10n_be",
                #~ "l10n_ma",
                "mrp_repair",
                "project",
                #~ "survey",Repeated module
                "auth_crypt",
                #~ "document_page",Repeated module
                #~ "l10n_be_coda",
                "l10n_multilang",
                "multi_company",
                "project_gtd",
                "warning",
                #"auth_ldap", #No test
                "document_webdav",
                #~ "l10n_be_hr_payroll",
                "l10n_mx",
                "note",
                "project_issue",
                "web_analytics",
                "auth_oauth",
                #~ "edi",Repeated module
                #~ "l10n_be_hr_payroll_account",
                #~ "l10n_nl",
                "note_pad",
                "project_issue_sheet",
                "web_linkedin",
                "auth_oauth_signup",
                #~ "email_template",Repeated module
                #~ "l10n_be_invoice_bba",
                #~ "l10n_pa",
                "pad",
                "project_long_term",
                "web_shortcuts",
                "purchase_requisition",
                "purchase_double_validation",
                "account_analytic_default",
                "oml",
                #End list of all oficial modules
                ],
    "author" : "Vauxoo",
    "description" : """
Install all apps needed to comply with Mexican laws plus all oficial modules 
===================================================

This module will install for you:
  
  -  oml module
  
  - And all oficial modules (account, stock, mrp...)
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
