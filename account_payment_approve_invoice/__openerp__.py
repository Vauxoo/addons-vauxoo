# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
###############Credits######################################################
#    Coded by: Vauxoo C.A. (Maria Gabriela Quilarque)
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
##############################################################################
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
#
##############################################################################
{
    "name": "Payment Approve", 
    "version": "0.1", 
    "author": "Vauxoo", 
    "category": "Generic Modules", 
    "description": """
Purchase Manager Payment Approve
================================

This module, allows to Purchase Manager Approve or Disapproves the pay to one invoice, through two buttons added in the supplier invoice.

Added message to block the invoice messaging when the invoice is Approve to Pay or Disapproves to Pay.

Also added permissions to buttons.

The description of two buttons:

    * Approve to Pay: Mark boolean To Pay when is activated.

.. image:: account_payment_approve_invoice/static/src/demo/button_approve.png
.
    * Disapproves to Pay: Uncheck boolean To Pay when is activated.

.. image:: account_payment_approve_invoice/static/src/demo/button_disapproves.png

""", 
    "website": "http://vauxoo.com", 
    "license": "", 
    "depends": [
        "base", 
        "account"
    ], 
    "demo": [], 
    "data": [
        "view/account_invoice_view.xml", 
        "security/account_security.xml", 
        "security/ir.model.access.csv"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}