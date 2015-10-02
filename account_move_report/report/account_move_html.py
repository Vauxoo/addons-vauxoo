# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# ##############Credits######################################################
#    Coded by: Luis Ernesto García (ernesto_gm@vauxoo.com)
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
from openerp.report import report_sxw
import time
from .webkit_parser_header_fix import HeaderFooterTextWebKitParser


class AccountMoveReportHtml(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(AccountMoveReportHtml, self).__init__(cr, uid, name,
                                                    context=context)
        self.localcontext.update({
            'time': time,
            'get_total_debit_credit': self.get_total_debit_credit,
        })

    def get_total_debit_credit(self, line_ids):
        sum_tot_debit = 0.00
        sum_tot_credit = 0.00
        for line in line_ids:
            sum_tot_debit += (line.debit)
            sum_tot_credit += (line.credit)
        return {
            'sum_tot_debit': sum_tot_debit, 'sum_tot_credit': sum_tot_credit}

HeaderFooterTextWebKitParser(
    'report.account.move.report.webkit',
    'account.move',
    'addons/report_account_move/report/account_move_report_html.mako',
    parser=AccountMoveReportHtml)
