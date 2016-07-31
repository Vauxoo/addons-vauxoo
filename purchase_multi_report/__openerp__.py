# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@vauxoo.com>
#              María Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#              Nhomar Hernandez          <nhomar@vauxoo.com>
#    Planified by: Humberto Arocha
#    Finance by: Vauxoo, C.A. http://vauxoo.com
#    Audited by: Humberto Arocha humberto@vauxoo.com
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
    "name": "Report Order customisation Vnzla",
    "version": "8.0.0.0.6",
    "author": "Vauxoo",
    "category": "Generic Modules/Others",
    "website": "http://wiki.openerp.org.ve/",
    "license": "",
    "depends": [
        "purchase",
        "multireport_base"
    ],
    "demo": [],
    "data": [
        "wizard/purchase_report_multicompany.xml",
        "purchase_report_view.xml"
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": False,
    "auto_install": False,
}
