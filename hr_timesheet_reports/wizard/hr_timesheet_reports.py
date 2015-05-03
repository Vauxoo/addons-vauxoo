# -*- encoding: utf-8 -*-
from openerp.osv import osv, fields


class fiscal_book_wizard(osv.osv_memory):

    _name = "hr.timesheet.reports.base"
    _columns = {
        'filter_id': fields.many2one(
            'ir.filters', 'Filter', help='Filter',
            domain=[('model_id',
                     '=',
                     'ref("model_hr_analytic_timesheet")')]),
    }

    def do_report(self, cr, uid, ids, context=None):
        my_data = self.read(cr, uid, ids, context=context)[0]
        datas = {
                'model': context.get('active_model', 'ir.ui.menu'),
                'ids': ids,
                'form': my_data,
                }
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'hr.timesheet.reports.base',
                'report_type': "webkit",
                'datas': datas,
                'string': "Hr timesheet reports base",
                'file': "hr_timesheet_reports/wizard/hr_timesheet_reports_base.mako",
                'nodestroy': True,
                }
