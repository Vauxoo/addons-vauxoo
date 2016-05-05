# coding: utf-8
# ##########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
# ###########################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
# ###########################################################################
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
"""File to added method and function to report Demo
"""

from openerp.report import report_sxw
from openerp.addons.report_webkit import webkit_report


class InvoiceReportDemoHtml(report_sxw.rml_parse):

    """Define methods that need the report
    """

    def __init__(self, cr, uid, name, context=None):
        """Initialization method
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param name: Ids to invoice's to print ticket
        @param context: A standard dictionary
        """
        if context is None:
            context = {}
        super(InvoiceReportDemoHtml, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
        })

webkit_report.WebKitParser(
    'report.invoice.report.demo.webkit', 'account.invoice',
    'addons/invoice_report_per_journal/report/invoice_report_demo.mako',
    parser=InvoiceReportDemoHtml)
