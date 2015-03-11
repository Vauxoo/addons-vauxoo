# -*- coding: utf-8 -*-
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

from openerp.osv import fields, osv
from openerp.tools.sql import drop_view_if_exists


class hr_timesheet(osv.Model):
    _inherit = "hr.analytic.timesheet"

    def _get_invoiceables_hours(self, cr, uid, ids, args, fields, context=None):
        context = context or {}
        res = {}
        for time_brw in self.browse(cr, uid, ids, context=context):
            hours = time_brw.unit_amount
            if time_brw.to_invoice:
                hours = time_brw.unit_amount - \
                    (time_brw.unit_amount * \
                    (time_brw.to_invoice.factor / 100))
            res.update({time_brw.id: hours})
        return res

    def _get_user_story(self, cr, uid, ids, args, fields, context=None):
        context = context or {}
        res = {}
        task_obj = self.pool.get('project.task')
        for time_brw in self.browse(cr, uid, ids, context=context):
            us_id = False
            task_ids = task_obj.\
                search(cr, uid,
                       [('work_ids.hr_analytic_timesheet_id', '=',
                         time_brw.id)])
            if task_ids:
                task_read = task_obj.read(cr, uid, task_ids[0],
                                          ['userstory_id'],
                                          load='_classic_write')
                us_id = task_read.get('userstory_id')
            res.update({time_brw.id: us_id})
        return res

    def _get_analytic_from_task(self, cr, uid, ids, context=None):
        context = context or {}
        cr.execute('''
                   SELECT array_agg(work.hr_analytic_timesheet_id) as a_id
                   FROM project_task AS task
                   INNER JOIN project_task_work AS work ON work.task_id=task.id
                   WHERE task.id {op} {tids}
                   '''.format(op=(len(ids) == 1) and '=' or 'in',
                              tids=(len(ids) == 1) and ids[0] or tuple(ids)))
        res = cr.dictfetchall()
        if res:
            res = res[0].get('a_id', []) or []
        return res

    _columns = {
        'invoiceables_hours': fields.function(_get_invoiceables_hours,
                                              type='float',
                                              store={
                                                  _inherit: (lambda s, c, u,
                                                             ids, cx={}: ids,
                                                             ['unit_amount',
                                                              'to_invoice'],
                                                             10)},
                                              string='Invoiceable Hours',
                                              help='Total hours to charge'),

        'userstory_id': fields.function(_get_user_story,
                                        type='many2one',
                                        relation='user.story',
                                        string='User Story',
                                        store={
                                            'project.task': \
                                            (_get_analytic_from_task,
                                             ['userstory_id'],
                                             10)
                                        },
                                        help="User Story set in the "
                                        "task of this TimeSheet"),
        'us_id': fields.related('userstory_id',
                                'id',
                                type='integer',
                                store=True,
                                string='User Story Code')
    }


class custom_timesheet(osv.Model):
    _name = "custom.timesheet"
    _order = "date desc"
    _auto = False

    def _get_invoiceables_hours(self, cr, uid, ids, args, fields, context=None):
        context = context or {}
        res = {}
        for time_brw in self.browse(cr, uid, ids, context=context):
            hours = time_brw.unit_amount
            if time_brw.to_invoice:
                hours = time_brw.unit_amount - \
                    (time_brw.unit_amount * \
                    (time_brw.to_invoice.factor / 100))
            res.update({time_brw.id: hours})
        return res

    _columns = {
        'date': fields.date('Date', readonly=True),
        'user_id': fields.many2one('res.users', 'User', readonly=True,
                                   select=True),
        'userstory': fields.integer('User Story', readonly=True),
        'analytic_id': fields.many2one('account.analytic.account', 'Project',
                                       readonly=True, select=True),
        'task_title': fields.char('Task Tittle', 128,
                                  help='Name of task related'),
        'userstory_id': fields.many2one('user.story', 'User Story',
                                        help='Code of User Story related '
                                        'to this analytic'),
        'name': fields.char('Description', 264, help='Description of the work'),

        'unit_amount': fields.float('Duration', readonly=True),
        'timesheet_id': fields.many2one('hr.analytic.timesheet',
                                        'TimeSheet', readonly=True,
                                        select=True),
        'to_invoice': fields.related('timesheet_id',
                                     'to_invoice',
                                     relation='hr_timesheet_invoice.factor',
                                     type='many2one',
                                     string='Invoiceable'),
        'invoiceables_hours': fields.function(_get_invoiceables_hours,
                                              type='float',
                                              string='Invoiceable Hours',
                                              help='Total hours to charge')
    }

    def init(self, cr):
        drop_view_if_exists(cr, 'custom_timesheet')
        cr.execute('''
            create or replace view custom_timesheet as (
                SELECT
                      work.id AS id,
                      work.date AS date,
                      work.user_id AS user_id,
                      us.id AS userstory_id,
                      us.id AS userstory,
                      analytic.id AS analytic_id,
                      task.name AS task_title,
                      work.name AS name,
                      work.hours AS unit_amount,
                      tsheet.id AS timesheet_id
                FROM project_task_work AS work
                LEFT JOIN hr_analytic_timesheet AS tsheet ON tsheet.id = work.hr_analytic_timesheet_id
                INNER JOIN project_task AS task ON task.id = work.task_id
                INNER JOIN user_story AS us ON us.id = task.userstory_id
                INNER JOIN project_project AS project ON project.id = task.project_id
                INNER JOIN account_analytic_account AS analytic ON analytic.id = project.analytic_account_id
        )''')
