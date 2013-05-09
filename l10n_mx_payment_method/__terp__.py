# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Coded by: isaac (isaac@vauxoo.com)
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
    "name" : "Agregado del método de pago al partner y a la factura",
    "version" : "1.0",
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    "description" : """Add "Payment Method" to partner and invoice, it's used by l10n_mx_facturae_22 module
    """,
    "website" : "www.vauxoo.com",
    "depends" : ["account",
        ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "security/payment_method.xml",
        "security/ir.model.access.csv",
        "pay_method_view_v5.xml",
        "partner_view.xml",
        "invoice_view_v5.xml",
        "data/payment_method_data.xml",
    ],
    "installable" : True,
    "active" : False,
}
