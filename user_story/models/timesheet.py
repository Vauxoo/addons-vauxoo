# -*- coding: utf-8 -*-
"""
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
"""

from openerp import models, fields, api
from openerp.tools.sql import drop_view_if_exists


class HrTimesheet(models.Model):
    _inherit = "hr.analytic.timesheet"

    invoiceables_hours = fields.Float(compute='_get_invoiceables_hours',
                                      store={_inherit: (lambda s: self.ids,
                                                        ['unit_amount',
                                                         'to_invoice'],
                                                         10)},
                                          string='Invoiceable Hours',
                                          help='Total hours to charge'),

    userstory_id = fields.Many2one(compute='_get_user_story',
                                    relation='user.story',
                                    string='User Story',
                                    store={
                                        'project.task':
                                        (_get_analytic_from_task,
                                         ['userstory_id'],
                                         10)
                                    },
                                    help="User Story set in the "
                                    "task of this TimeSheet"),
    us_id = fields.Integer(related='userstory_id',
                           store=True,
                           string='User Story Code')

    def _get_invoiceables_hours(self):  # pylint: disable=W0621

        res = {}
        for time_brw in self.browse():
            hours = time_brw.unit_amount
            if time_brw.to_invoice:
                hours = time_brw.unit_amount - \
                    (time_brw.unit_amount *
                     (time_brw.to_invoice.factor / 100))
            res.update({time_brw.id: hours})
        return res

    def _get_user_story(self):  # pylint: disable=W0621

        res = {}
        task_obj = self.env['project.task']
        for time_brw in self:
            us_id = False
            task_recs = task_obj.search([('work_ids.hr_analytic_timesheet_id', '=',
                                         time_brw.id)])
            if task_recs:
                task_read = task_obj.read(cr, uid, task_ids[0],
                                          ['userstory_id'],
                                          load='_classic_write')
                us_id = task_read.get('userstory_id')
            res.update({time_brw.id: us_id})
        return res

    def _get_analytic_from_task(self):

        self.env.cr.execute('''
                   SELECT array_agg(work.hr_analytic_timesheet_id) as a_id
                   FROM project_task AS task
                   INNER JOIN project_task_work AS work ON work.task_id=task.id
                   WHERE task.id {op} {tids}
                   '''.format(op=(len(self.ids) == 1) and '=' or 'in',
                              tids=(len(self.ids) == 1) and self.ids[0] or tuple(self.ids)))
        res = self.env.cr.dictfetchall()
        if res:
            res = res[0].get('a_id', []) or []
        return res


class CustomTimesheet(models.Model):
    _name = "custom.timesheet"
    _order = "date desc"
    _auto = False

    date = fields.Date('Date', readonly=True),
    user_id = fields.Many2one('res.users', 'User', readonly=True, select=True),
    userstory = fields.Integer('User Story', readonly=True),
    analytic_id = fields.Many2one('account.analytic.account', 'Project', readonly=True, select=True),
    task_title = fields.Char('Task Tittle', 128, help='Name of task related'),
    userstory_id = fields.Many2one('user.story', 'User Story',
                                   help='Code of User Story related to this analytic'),
    name = fields.Char('Description', 264, help='Description of the work'),
    unit_amount = fields.Float('Duration', readonly=True),
    timesheet_id = fields.Many2one('hr.analytic.timesheet', 'TimeSheet', readonly=True, select=True),
    to_invoice = fields.related('timesheet_id', 'to_invoice',
                                 relation='hr_timesheet_invoice.factor',
                                 type='many2one',
                                 string='Invoiceable'),
    invoiceables_hours = fields.Float(compute='_get_invoiceables_hours',
                                      string='Invoiceable Hours',
                                      help='Total hours to charge')

    def _get_invoiceables_hours(self):  # pylint: disable=W0621

        res = {}
        for time_brw in self.search():
            hours = time_brw.unit_amount
            if time_brw.to_invoice:
                hours = time_brw.unit_amount - \
                    (time_brw.unit_amount *
                     (time_brw.to_invoice.factor / 100))
            res.update({time_brw.id: hours})
        return res

    def init(self):

        drop_view_if_exists(self.env.cr, 'custom_timesheet')
        self.env.cr.execute('''
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
                LEFT JOIN hr_analytic_timesheet AS tsheet
                   ON tsheet.id = work.hr_analytic_timesheet_id
                INNER JOIN project_task AS task ON task.id = work.task_id
                INNER JOIN user_story AS us ON us.id = task.userstory_id
                INNER JOIN project_project AS project
                   ON project.id = task.project_id
                INNER JOIN account_analytic_account AS analytic
                   ON analytic.id = project.analytic_account_id
        )''')
