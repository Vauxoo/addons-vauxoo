# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info moylop260 (moylop260@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Coded by: Isaac Lopez (isaac@vauxoo.com)
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
    "name" : "Add field discount to a partner and wizard apply discount on invoice",
    "version" : "1.0",
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    "description" : """Add field discount to a partner and discount fields on invoice. It's apply discount in all lines when you press compute taxes button. Add discount and motive discount fields on xml(CFD and CFDI)""",
    "website" : "http://www.vauxoo.com/",
    "license" : "AGPL-3",
    "depends" : ["l10n_mx_facturae_pac_sf"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["partner_view.xml",
                    "invoice_view.xml",
                    ],
    "installable": False,
    "active": False,
}
