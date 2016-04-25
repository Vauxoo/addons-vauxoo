# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.report import report_sxw


class AccountInvoice2(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(AccountInvoice2, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cg': self.context_get,
        })

    def context_get(self):
        """Description about method

        @param obj: object passed from report to be process

        @return: return a result
        """
        print "COLOOOOOOOOOOOOOOOOOO"
        return self.context


report_sxw.report_sxw(
    'report.account.invoices.amd',
    'account.invoice',
    'addons/invoice_report_multicompany/report/account_print_invoices.rml',
    parser=AccountInvoice2
)
