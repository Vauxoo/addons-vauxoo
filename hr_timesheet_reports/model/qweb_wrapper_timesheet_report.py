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

import logging
from openerp.report import report_sxw
from openerp.osv import osv

_logger = logging.getLogger(__name__)


class TimesheetReportQwebHtml(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        super(TimesheetReportQwebHtml, self).\
            __init__(cr, uid, name, context=context)
        self.localcontext.update({
            'translatable': True,
            'get_records': self._get_records,

        })

    def _get_records(self, timesheet):
        records = self.objects._get_print_data('a', 'b')
        records = records[timesheet.id]
        return records


class TimesheetReportQwebPdfReport(osv.AbstractModel):

    # _name = `report.` + `report_name`
    _name = 'report.hr_timesheet_reports.timesheet_report_vauxoo'

    # this inheritance will allow to render this particular report
    _inherit = 'report.abstract_report'
    _template = 'hr_timesheet_reports.timesheet_report_vauxoo'
    _wrapped_report_class = TimesheetReportQwebHtml

    def render_html(self, cr, uid, ids, data=None, context=None):
        context = dict(context or {})
        context.update({'translatable': True})
        return super(TimesheetReportQwebPdfReport, self).\
            render_html(cr, uid, ids, data=data, context=context)
