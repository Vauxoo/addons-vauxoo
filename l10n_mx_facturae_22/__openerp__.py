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
    "name" : "Migracion de Factura Electronica para Mexico (CFD) de 2.0 a 2.2",
    "version" : "1.0",
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    "description" : """Upgrade CFD 2.0 to CFD 2.2. If you are working with OpenERP version < 6.1 you need install the module: l10n_mx_res_partner_bank_currency
    """,
    "website" : "www.vauxoo.com",
    "license" : "AGPL-3",
    "depends" : ["l10n_mx_facturae",
                "partner_bank_last_digits",
                "l10n_mx_facturae_22_regimen_fiscal",
                "l10n_mx_facturae_22_payment_method",
                "invoice_currency_chgdft",
                "l10n_mx_invoice_acc_payment",
        ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "invoice_view.xml",
    ],
    "installable" : True,
    "active" : False,
}
