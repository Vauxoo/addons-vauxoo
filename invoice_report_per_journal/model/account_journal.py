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
"""Method to added field report_id in the journal
"""
from openerp.osv import fields, osv


class InvoiceReportPerJournal(osv.Model):

    """invoice_report_per_journal
    """

    _inherit = 'account.journal'
    _columns = {
        'invoice_report_id': fields.many2one(
            'ir.actions.report.xml', 'Invoice Report', required=False,
            domain="[('model','=','account.invoice')]"),
    }
