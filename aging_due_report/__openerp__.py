# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# ##############Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Rafael Silva <rsilvam@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#     by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
{
    "name": "Customer's Due Report",
    "version": "9.0.0.0.6",
    "author": "Vauxoo",
    "category": "Generic Modules/Others",
    "website": "http://www.vauxoo.com/",
    "license": "",
    "depends": [
        "account",
        "controller_report_xls",
    ],
    "demo": [],
    "data": [
        "data/aging_due_report_paper_format.xml",
        "data/aging_due_report_style.xml",
        "report/aging_due_report_qweb.xml",
        "report/aging_detail_due_report_qweb.xml",
        "report/detail_due_report_qweb.xml",
        "report/customer_formal_due_report_qweb.xml",
        "report/supplier_formal_due_report_qweb.xml",
        "views/wizard.xml",
        "views/report.xml"
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "external_dependencies": {
        "python": [
            'pandas',
        ]
    }
}
