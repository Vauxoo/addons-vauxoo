# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Jorge Naranjo (jorge_nr@vauxoo.com)
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
    "name" : "Tests Invoice and Payroll CFDI Pacs SF and Finkok",
    "version" : "1.0",
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    "description" : """
This module execute all test yaml of invoice and payroll CFDI.
""",
    "website" : "http://www.vauxoo.com/",
    "license" : "AGPL-3",
    "depends" : [
        "l10n_mx_facturae_pac_sf",
        "l10n_mx_facturae_pac_finkok",
        "l10n_mx_payroll_base",
        ],
    "demo" : [],
    "data" : [],
    "test" : [
        #~ "test/test_facturae_pac_sf.yml",
        #~ "test/test_payroll_pac_sf.yml",
        #~ "test/test_facturae_pac_finkok.yml",
        #~ "test/test_payroll_pac_finkok.yml",
        "test/test_facturae_pac_all_cancel_from_attachment.yml",
        "test/test_facturae_pac_all_cancel_from_invoce.yml",
    ],
    "installable" : True,
    "active" : False,
}
