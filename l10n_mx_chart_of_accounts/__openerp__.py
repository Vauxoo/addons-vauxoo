# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo S.A. de C.V. (<http://www.vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Alejandro Negrin anegrin@vauxoo.com,
#    Planified by: Alejandro Negrin, Humberto Arocha, Moises Lopez
#    Finance by: Vauxoo S.A. de C.V.
#    Audited by: Humberto Arocha (hbto@vauxoo.com) y Moises Lopez (moylop260@vauxoo.com)
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

{
    "name" : "Vauxoo Chart of Account Mexico",
    "version" : "1.0",
    "author" : "Vauxoo",
    "category" : "Localization/Account Charts",
    "description": """
Esta es una propuesta de catalogo de cuentas para México y la mayoria de los paises de America Latina, basado en el plan de cuentas unico Colombiano
    """,
    "website" : "http://www.vauxoo.com/",
    "depends" : ["account", "base_vat", "account_chart"],
    "demo_xml" : [],
    "update_xml" : ['account_tax_code.xml',"account_chart.xml",'account_tax.xml',"l10n_chart_mx_wizard.xml"],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

