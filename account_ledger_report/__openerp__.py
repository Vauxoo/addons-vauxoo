# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Maria Gabriela Quilarque <gabrielaquilarque97@gmail.com>
#              Luis E. Escobar V. <luis@vauxoo.com>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
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
    "name": "Account Ledger Report",
    "version": "0.1",
    "depends": ["base","account"],
    "author": "Vauxoo",
    "description" : """
    Module that replace original ledger report to optimize the printing space.
    The reports changed are:
        - account_general_ledger.rml
        - account_general_ledger_landscape.rml
        - account_partner_ledger.rml
        - account_partner_ledger_other.rml
    In these reports were eliminated:
        - Journal (header)
        - Partner field
        - Ref field
 """,
    "website": "http://vauxoo.com",
    "category": "Generic Modules/Accounting",
    "init_xml": [
    ],
    "demo_xml": [
    ],
    "update_xml": [
        'acc_ledger_report.xml',
    ],
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
