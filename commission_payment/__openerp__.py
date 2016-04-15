# coding: utf-8
##############################################################################
#
# Copyright (c) 2010 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Humberto Arocha <humbertoarocha@gmail.com>
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
{
    "name": "Salespeople Commission based on Payments",
    "version": "9.0.0.0.6",
    "author": "Vauxoo",
    "category": "Generic Modules/Others",
    "website": "http://www.vauxoo.com",
    "license": "",
    "depends": [
        "base",
        "account",
        "product_historical_price",
        "mail",
        "baremo",
        "message_post_model",
        "report",
    ],
    "demo": [
        "demo/account_invoice_demo.xml",
    ],
    "data": [
        "security/commission_payment_security.xml",
        "security/ir.model.access.csv",
        "report/layouts.xml",
        "report/template.xml",
        "data/report_paperformat.xml",
        "view/commission_report.xml",
        "view/commission_view.xml",
        "view/account_view.xml",
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
