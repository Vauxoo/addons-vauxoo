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
    "name" : "Agrega el Regimen Fiscal al partner",
    "version" : "1.0",
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    "description" : """Add "Regimen Fiscal" to partner, it's used by l10n_mx_facturae_22 module
    """,
    "website" : "www.vauxoo.com",
    "depends" : ["base",
        ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "security/regimen_fiscal.xml",
        "security/ir.model.access.csv",
        "regimen_fiscal_v5.xml",
        "partner_view.xml",
        "data/regimen_fiscal_data.xml",
    ],
    "installable" : True,
    "active" : False,
}
