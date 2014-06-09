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
class custom_timesheet(osv.Model):
    _name = "custom.timesheet"
    _order = "date desc"
    _auto = False
    _columns = {
        'date': fields.date('Date', readonly=True),
        'user_id': fields.many2one('res.users', 'User',
                readonly=True, select=True),
        'userstory': fields.integer('User Story', readonly=True),
        'analytic_id': fields.many2one('account.analytic.account', 'Project',
                readonly=True, select=True),
        'task_title':fields.char('Task Tittle', 128,
                                 help='Name of task related'),
        'userstory_id':fields.many2one('user.story','User Story',
                              help='Code of User Story related to this '
                                   'analytic'),
        'name':fields.char('Description', 264, help='Description of the work'),

        'unit_amount': fields.float('Duration', readonly=True),
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
                      work.hours AS unit_amount
                FROM project_task_work AS work
                INNER JOIN project_task AS task ON task.id = work.task_id
                INNER JOIN user_story AS us ON us.id = task.userstory_id
                INNER JOIN project_project AS project ON project.id = task.project_id
                INNER JOIN account_analytic_account AS analytic ON analytic.id = project.analytic_account_id
        )''')
