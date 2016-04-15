# coding: utf-8
# ######################################################################## #
#    Module Writen to OpenERP, Open Source Management Solution             #
#    Copyright (C) Vauxoo (<http://vauxoo.com>).                           #
#    All Rights Reserved                                                   #
# ##############Credits################################################### #
#    Coded by: Sabrina Romero (sabrina@vauxoo.com)                         #
#    Planified by: Nhomar Hernandez (nhomar@vauxoo.com)                    #
#    Finance by: COMPANY NAME <EMAIL-COMPANY>                              #
#    Audited by: author NAME LASTNAME <email@vauxoo.com>                   #
# ######################################################################## #
#    This program is free software: you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation, either version 3 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>. #
# ######################################################################## #
{
    "name": "Account Invoice Per Journal Report",
    "version": "9.0.0.1.6",
    "author": "Vauxoo",
    "category": "Generic Modules",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "account",
        "report_webkit"
    ],
    "demo": [],
    "data": [
        "data/data.xml",
        "view/account_journal_view.xml",
        "wizard/invoice_report_per_journal.xml",
        "view/account_invoice_view.xml",
        "report/invoice_report_demo.xml"
    ],
    "test": [
        "test/invoice_report_per_journal.yml"
    ],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
}
