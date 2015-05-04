# -*- encoding: utf-8 -*-
from openerp.osv import osv, fields
from openerp.tools.safe_eval import safe_eval

def clean_name(name):
    import re
    exp = r'\[.*?\]'
    text = name.strip()
    found = re.findall(exp, text)
    if found:
        for f in found:
            text = text.replace(f, '').strip()
    words = text.split(' ')
    if len(words) > 2:
        text = ' '.join([words[0], words[2]])
    return text


class fiscal_book_wizard(osv.osv_memory):

    _name = "hr.timesheet.reports.base"
    _rec_name='filter_id'

    def _prepare_data(self, record):
        return {
                'author': clean_name(record.user_id.name),
                'description': record.name,
                'duration': record.unit_amount,
                'date': record.date,
                }

    def _get_print_data(self, cr, uid, ids, name, args, context=None):
        res = {}
        for wzd in self.browse(cr, uid, ids, context=context):
            res[wzd.id] = self._get_result_ids(cr, uid, ids, context=context)
        return res

    def _get_result_ids(self, cr, uid, ids, context=None):
        res = []
        wzr_brw = self.browse(cr, uid, ids, context=context)[0]
        domain = wzr_brw.filter_id.domain
        timesheet_obj = self.pool.get('hr.analytic.timesheet')
        dom = [tuple(d) for d in safe_eval(domain)]
        timesheet_ids = timesheet_obj.search(cr, uid, dom, context=context)
        timesheet_brws = timesheet_obj.browse(cr, uid, timesheet_ids,
                                              context=context)
        res = [self._prepare_data(tb) for tb in timesheet_brws]
        return res

    _columns = {
        'filter_id': fields.many2one(
            'ir.filters', 'Filter', help='Filter',
            domain=[('model_id', 'ilike', 'hr.analytic.timesheet')]),
        'records': fields.function(_get_print_data, string='Records', type="text")
    }

    def do_report(self, cr, uid, ids, context=None):
        my_data = self.read(cr, uid, ids, context=context)[0]
        return {
                'type': 'ir.actions.report.xml',
                'name': 'hr.timesheet.reports.explain',
                'report_name': 'hr.timesheet.reports.base',
                'report_type': "webkit",
                'string': "Hr timesheet reports base",
                'file': "hr_timesheet_reports/wizard/hr_timesheet_reports_base.mako",
                'nodestroy': True,
                }
