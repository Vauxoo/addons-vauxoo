# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# #############Credits#########################################################
#    Coded by: Jose Suniaga <josemiguel@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your
#    option) any later version.
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
    "name": "Update Purchase RFQ using XLS",
    "version": "1.6",
    "author": "Vauxoo",
    "category": "Purchase",
    "website": "http://www.vauxoo.com/",
    "license": "LGPL-3",
    "depends": [
        "report",
        "purchase",
        "controller_report_xls",
    ],
    "external_dependencies": {
        "python": [
            "xlrd",
        ]
    },
    "demo": [],
    "data": [
        "view/wizard.xml",
        "report/layouts.xml",
        "report/template.xml",
        "view/report.xml",
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
}
