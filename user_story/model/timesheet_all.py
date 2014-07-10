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
import time
import datetime

from openerp.osv import fields, osv
from openerp import pooler
from openerp import tools
from openerp.tools.translate import _

from openerp.tools.sql import drop_view_if_exists

class custom_timesheet_all(osv.Model):
    _name = "custom.timesheet.all"
    _order = "date desc"
    _auto = False
    
    _columns = {
        'period': fields.char('Period', 128, 
                    help='Period for the date of summary work.'),
        'date': fields.date('Date', readonly=True, 
                    help='Date of summary work.'),
        'analytic_id': fields.many2one('account.analytic.account', 'Project',
                    readonly=True, select=True),
        'userstory': fields.integer('User Story', readonly=True, 
                    help='User history id of user history assigned on task.'),
        'task_id': fields.many2one('project.task', 'Task title',
                    readonly=True, select=True, help='Project task title.'),
        'user_id': fields.many2one('res.users', 'User',
                    readonly=True, select=True, help='User of summary work.'),
        'name': fields.char('Description', 264, help='Description of the summary work.'),
        'unit_amount': fields.float('Duration', readonly=True, help='Time spent on work.'),
        'invoiceable': fields.many2one('hr_timesheet_invoice.factor', 'Invoiceable',
                    readonly=True, help='Definition of invoicing status of the line.'),
    }

    def init(self, cr):
        drop_view_if_exists(cr, 'custom_timesheet_all')
        cr.execute('''
            create or replace view custom_timesheet_all as (
                SELECT
                    work.id AS id,
                    to_char(work.date,'MM/YYYY') AS period,
                    work.date AS date,
                    analytic.id AS analytic_id,
                    us.id AS userstory,
                    task.id AS task_id,
                    work.user_id AS user_id,
                    work.name AS name,
                    work.hours AS unit_amount,
                    acc_anal_line.to_invoice AS invoiceable
                FROM project_task_work AS work
                LEFT JOIN hr_analytic_timesheet AS tsheet ON tsheet.id = work.hr_analytic_timesheet_id
                LEFT JOIN account_analytic_line AS acc_anal_line ON acc_anal_line.id = tsheet.line_id
                LEFT JOIN account_analytic_account AS analytic ON analytic.id = acc_anal_line.account_id
                LEFT JOIN project_task AS task ON task.id = work.task_id
                LEFT JOIN user_story AS us ON us.id = task.userstory_id
        )''')
