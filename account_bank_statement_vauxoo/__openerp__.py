# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Coded and Planified by Nhomar Hernandez <nhomar@vauxoo.com>
#
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
    "name" : "Fixes and Imrpovements to Bank Statement management",
    "version" : "0.1",
    "depends" : ["account",],
    "author" : "Vauxoo",
    "description" : """
Improve management of Bank Statement.
=====================================
    1.- Import directly from files given by banks.
        a.- Costa Rica Banks.
            Banco Nacional (CRC).
            Banco Nacional (USD).
        b.- Mexican Banks.
        c.- Venezuelan Banks.
            Banco Exterior #TODO
    2.- 
                    """,
    "website" : "http://vauxoo.com",
    "category" : "Accounting & Finance",
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "security/bank_statement_security.xml",
        "security/ir.model.access.csv",
        "view/account_bank_statement_view.xml",
        "view/account_invoice_view.xml",
        "view/account_journal_view.xml",
        "data/data.xml",
    ],
    "active": False,
    "images": [],
    "installable": True,
}
