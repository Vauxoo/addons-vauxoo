# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Financed by: http://www.sfsoluciones.com (aef@sfsoluciones.com)
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
    "name" : "Creacion de Factura Electronica para Mexico (CFDI-2011) - PAC Solucion Factible",
    "version" : "1.0",
    "author" : "Vauxoo & Sfsoluciones",
    "category" : "Localization/Mexico",
    "description" : """This module creates interface for e-invoice files from invoices with Solucion Factible.
Ubuntu Package Depends:
    sudo apt-get install python-soappy
""",
    "website" : "http://www.vauxoo.com/",
    "license" : "AGPL-3",
    "depends" : ["l10n_mx_facturae_groups", "l10n_mx_params_pac", 
        "l10n_mx_account_tax_category",
        "l10n_mx_facturae_report",
        "l10n_mx_facturae_seq", 
        "l10n_mx_ir_attachment_facturae",
        "l10n_mx_facturae_pac",
        "l10n_mx_facturae_group_show_wizards",
        "l10n_mx_settings_facturae",
        ],
    "demo" : [
        "demo/l10n_mx_facturae_pac_sf_demo.xml",
        "demo/l10n_mx_facturae_seq_demo.xml",
        "demo/account_invoice_cfdi_pac_sf_demo.xml",
    ],
    "data" : [
        #"security/l10n_mx_facturae_pac_sf_security.xml",
        "wizard/wizard_cancel_invoice_pac_sf_view.xml",
        "wizard/wizard_export_invoice_pac_sf_view_v6.xml",
    ],
    "test" : [
        "test/account_invoice_cfdi_pac_sf.yml",
    ],
    "installable" : True,
    "active" : False,
}
