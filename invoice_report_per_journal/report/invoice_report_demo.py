# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
############################################################################
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

from openerp.report import report_sxw
from openerp import pooler
from openerp.tools.translate import _
from openerp import tools
from openerp import tests
from openerp.osv import osv
from openerp import netsvc
import openerp
from report_webkit import webkit_report
import datetime

class invoice_report_demo_html(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(invoice_report_demo_html, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
        })

webkit_report.WebKitParser('report.invoice.report.demo.webkit',
            'account.invoice',
            'addons/invoice_report_per_journal/report/invoice_report_demo.mako',
            parser=invoice_report_demo_html)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
