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
    "name" : "l10n_mx_partner_address",
    "version" : "1.0",
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    "description" : """This module adds the fields: 'l10n_mx_street3','l10n_mx_street4','l10n_mx_city2' used in México address. 
    You can see this fields in partner form following the next steps:
        1.- The company's country needs to be México
        2.- The user must be assigned a company with country México defined

        This is very usable if you are working with multicompany schema.
    """,
    "website" : "http://www.vauxoo.com/",
    "license" : "AGPL-3",
    "depends" : [
            "base",
            "l10n_mx_states",
            "l10n_mx_regimen_fiscal",
        ],
    "demo" : ["demo/l10n_mx_partner_address_demo.xml",],
    "data" : [
        'country_data.xml',
        'res_company_view_inherit.xml',
    ],
    "installable" : True,
    "active" : False,
}
