# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://moylop.blogspot.com/
#    All Rights Reserved.
#    info moylop260 (moylop260@hotmail.com)
############################################################################
#    Coded by: moylop260 (moylop260@hotmail.com)
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
    "name" : "Creacion de Factura Electronica para Mexico (CBB)",
    "version" : "1.0",
    "author" : "moylop260@hotmail.com",
    "category" : "Localization/Mexico",
    "description" : """This module creates e-invoice files from invoices with standard CBB of Mexican SAT.
Codigo de Barras Bidimensional.
http://www.sat.gob.mx/sitio_internet/asistencia_contribuyente/principiantes/comprobantes_fiscales/66_19204.html
http://www.sat.gob.mx/sitio_internet/asistencia_contribuyente/principiantes/comprobantes_fiscales/66_19084.html
    """,
    "website" : "http://moylop.blogspot.com/",
    "license" : "AGPL-3",
    "depends" : ["account", "base_vat", "document", 
            "sale",#no depende de "sale" directamente, pero marca error en algunas versiones
            "l10n_mx_partner_address",
            "l10n_mx_invoice_datetime",
            "l10n_mx_invoice_tax_ref",
            "l10n_mx_facturae_seq",
        ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'security/ir.model.access.csv',
        "l10n_mx_facturae_report.xml",
        #"ir_sequence_view.xml",
        "res_company_view.xml",
    ],
    "installable" : True,
    "active" : False,
}
