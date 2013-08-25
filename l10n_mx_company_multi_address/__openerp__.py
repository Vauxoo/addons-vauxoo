# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com/
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
    "name" : "Multiaddress para una misma compañia",
    "version" : "1.0",
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    "description" : """This module allows the management of multiaddress for "factura electronica" whitout multicompany scheme
    """,
    "website" : "http://www.vauxoo.com/",
    "license" : "AGPL-3",
    "depends" : ["account", "l10n_mx_states", "l10n_mx_partner_address",
        ],
    "demo" : ["demo/l10n_mx_company_multi_address_demo.xml",],
    "data" : [
        #'security/ir.model.access.csv',
        "invoice_view_address.xml",
        #"ir_sequence_view.xml",
        #"res_company_view6.xml",
        #"invoice_view.xml",
        "res_company_view.xml",
        "account_journal_view.xml",
        #"partner_address_view.xml",
    ],
    "installable" : True,
    "active" : False,
}
