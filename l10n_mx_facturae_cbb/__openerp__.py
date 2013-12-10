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
    "name" : "Creacion de Factura Electronica para Mexico (CBB)",
    "version" : "1.0",
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    "description" : """This module creates e-invoice files from invoices with standard CBB of Mexican SAT.
Codigo de Barras Bidimensional.
http://www.sat.gob.mx/sitio_internet/asistencia_contribuyente/principiantes/comprobantes_fiscales/66_19204.html
http://www.sat.gob.mx/sitio_internet/asistencia_contribuyente/principiantes/comprobantes_fiscales/66_19084.html
    """,
    "website" : "http://www.vauxoo.com/",
    "license" : "AGPL-3",
    "depends" : ["l10n_mx_facturae_groups", "account",
            "base_vat",
            "document",
            "sale",#no depende de "sale" directamente, pero marca error en algunas versiones
            "l10n_mx_partner_address",
            "l10n_mx_invoice_datetime",
            "l10n_mx_facturae_seq",
            "l10n_mx_company_cif",
            "l10n_mx_invoice_amount_to_text",
            "l10n_mx_ir_attachment_facturae",
            "l10n_mx_facturae_report",
            "l10n_mx_company_multi_address",
            "l10n_mx_settings_facturae",
        ],
    "demo" : ["demo/l10n_mx_facturae_seq_demo.xml",
              "demo/account_invoice_cbb_demo.xml",
              ],
    "data" : [
        #'security/l10n_mx_facturae_cbb_security.xml',
        'ir_sequence_view_v6.xml',
    ],
    "test" : ["test/account_invoice_cbb.yml"],
    "installable" : True,
    "active" : False,
}
