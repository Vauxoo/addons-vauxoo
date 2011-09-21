# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    author.name@company.com
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
import time
from report import report_sxw
from osv import osv
from tools.translate import _
from report import pyPdf

class amd_computadoras_sale(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(amd_computadoras_sale, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'hello': self._hello,
        })
    def _hello(self,p):
        print "estoy en hello"
        output = pyPdf.PdfFileWriter()
        print output
        return "Hello World %s" % output

report_sxw.report_sxw(
'report.sale_m321_c_report',
'sale.order',
'addons/sale_order_report/report/amd_computadoras_sale_report.rml',
parser=amd_computadoras_sale)
