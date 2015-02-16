#!/usr/bin/python
# -*- encoding: utf-8 -*-
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
    "version": "0.1",
    "author": "Vauxoo",
    "category": "Generic Modules/Others",
    "description": """
This module will allow you to get:
A Customer's Formal Due Report,
A Customer's Detail Due Report,
A Customer's Aging Due Report.
A Supplier's Formal Due Report,
A Supplier's Detail Due Report,
A Supplier's Aging Due Report.
""",
    "website": "http://www.vauxoo.com/",
    "license": "",
    "depends": [
        "account",
        "report_webkit"
    ],
    "demo": [],
    "data": [
        "data/aging_due_report_paper_format.xml",
        "views/customer_aging_due_report_qweb.xml",
        "views/customer_formal_due_report_qweb.xml",
        "views/customer_detail_due_report_qweb.xml",
        "views/supplier_aging_due_report_qweb.xml",
        "views/supplier_detail_due_report_qweb.xml",
        "views/supplier_formal_due_report_qweb.xml",
        "views/aging_due_report.xml"
        # "report/ing_due_report.xml",
        # "data/aging_due_webkit_header.xml",
        # "data/customer_formal_due_webkit_header.xml",
        # "data/customer_detail_due_webkit_header.xml",
        # "data/supplier_aging_due_webkit_header.xml",
        # "data/supplier_formal_due_webkit_header.xml",
        # "data/supplier_detail_due_webkit_header.xml",
        # "report/aging_due_report_webkit.xml"
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "active": False
}
