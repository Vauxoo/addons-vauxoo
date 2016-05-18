# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Rafael Silva <rsilvam@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
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
##########################################################################


import time
from datetime import datetime

from openerp.report import report_sxw
from openerp.osv import osv


class AgingParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(AgingParser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'int': int,
            'datetime': datetime,
        })


class AgingParserQwebPdfReport(osv.AbstractModel):
    _name = 'report.aging_due_report.aging_due_report_qweb'
    _inherit = 'report.abstract_report'
    _template = 'aging_due_report.aging_due_report_qweb'
    _wrapped_report_class = AgingParser


class AgingDetailParserQwebPdfReport(osv.AbstractModel):
    _name = 'report.aging_due_report.aging_detail_due_report_qweb'
    _inherit = 'report.abstract_report'
    _template = 'aging_due_report.aging_detail_due_report_qweb'
    _wrapped_report_class = AgingParser


class FormalParserQwebPdfReport(osv.AbstractModel):
    _name = 'report.aging_due_report.formal_due_report_qweb'
    _inherit = 'report.abstract_report'
    _template = 'aging_due_report.formal_due_report_qweb'
    _wrapped_report_class = AgingParser


class DetailParserQwebPdfReport(osv.AbstractModel):
    _name = 'report.aging_due_report.detail_due_report_qweb'
    _inherit = 'report.abstract_report'
    _template = 'aging_due_report.detail_due_report_qweb'
    _wrapped_report_class = AgingParser


class SupplierFormalParserQwebPdfReport(osv.AbstractModel):
    _name = 'report.aging_due_report.supplier_formal_due_report_qweb'
    _inherit = 'report.abstract_report'
    _template = 'aging_due_report.supplier_formal_due_report_qweb'
    _wrapped_report_class = AgingParser
