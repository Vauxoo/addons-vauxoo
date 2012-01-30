 # -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Javier Duran javier@vauxoo.com
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

{
    "name" : "Report Profit",
    "version" : "0.2",
    "depends" : ["base","product", "purchase"],
    "author" : "Vauxoo",
    "description" : """
        Performs the equivalent of a third unit for the analysis of sales.

 """,
    "website" : "http://vauxoo.com",
    "category" : "Localization",
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "security/ir.model.access.csv",
        "unit_analisys_view.xml",
    ],
    "active": False,
    "installable": True,
}
