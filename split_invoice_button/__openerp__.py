# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: nhomar@openerp.com.ve,
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
    "name" : "Split Invoice Button",
    "version" : "0.1",
    "depends" : ["l10n_ve_split_invoice"],
    "author" : "Vauxoo",
    "description" : """
For legal reasons in Venezuela we need just ONE invoice per page,
so this button allows the user view all generated invoices with the l10n_ve_split_invoice module
 """     ,
    "website" : "http://vauxoo.com",
    "category" : "Localization",
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "view/invoice_view.xml",
        "security/split_invoice_security.xml",
        "security/ir.model.access.csv",
    ],
    "active": False,
    "installable": True,
}
