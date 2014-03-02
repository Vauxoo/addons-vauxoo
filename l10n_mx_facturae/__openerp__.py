# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Launchpad Project Manager for Publication: Nhomar Hernandez - nhomar@vauxoo.com
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
    "name" : "Creacion de Factura Electronica para Mexico (CFD)",
    "version" : "1.0",
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    "description" : """This module creates e-invoice files from \
    invoices with standard CFD-2010 of Mexican SAT.
Requires the following programs:
  xsltproc
    Ubuntu insall with:
        sudo apt-get install xsltproc

  openssl
      Ubuntu insall with:
        sudo apt-get install openssl

  xmlstarlet
      Ubuntu insall with:
        sudo apt-get install xmlstarlet
    """,
    "website" : "http://www.vauxoo.com/",
    "license" : "AGPL-3",
    
    "depends" : [ "l10n_mx_facturae_groups", "account", "base_vat", 
            "document",
            "l10n_mx_facturae_lib",
            "l10n_mx_facturae_cer",
            "l10n_mx_invoice_datetime",
            "l10n_mx_account_tax_category",
            "l10n_mx_facturae_seq",
            "l10n_mx_company_cif",
            "l10n_mx_partner_address",
            "l10n_mx_invoice_amount_to_text",
            "l10n_mx_ir_attachment_facturae",
            "sale",#no depende de "sale" directamente, pero marca error en algunas versiones
            "l10n_mx_notes_invoice",
            "l10n_mx_res_partner_bank",
            "l10n_mx_regimen_fiscal",
            "l10n_mx_payment_method",
            "l10n_mx_invoice_currency_chgdft",
            "l10n_mx_base_vat_split",
            "l10n_mx_facturae_report",
            "l10n_mx_facturae_group_show_wizards",
            "l10n_mx_settings_facturae",
            "l10n_mx_params_pac"
        ],
    "demo" : [
        "demo/l10n_mx_facturae_seq_demo.xml",
        "demo/account_invoice_cfd_demo.xml",
    ],
    "data" : [
        #'security/l10n_mx_facturae_security.xml',
        #'security/ir.model.access.csv',
        #"l10n_mx_facturae_report.xml",
        "wizard/wizard_invoice_facturae_txt_v6_view.xml",
        "wizard/wizard_invoice_facturae_xml_v6_view.xml",
        "wizard/installer_view.xml",
        #"invoice_view.xml",
    ],
    "test" : [
        "test/account_invoice_cfd.yml",
    ],
    "installable" : True,
    "active" : False,
}
