# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
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
'''
This file loads the necessary information for the custom task view.
'''
from openerp.osv import fields, osv
from openerp.tools.sql import drop_view_if_exists


class custom_project_task(osv.Model):

    '''
    Class that contains the methods needed to return the data to the view.
    '''
    _name = "custom.project.task"
    _auto = False

    _columns = {
        'analytic_id': fields.many2one('account.analytic.account', 'Project',
                                       readonly=True, select=True),
        'counter': fields.integer('Num', readonly=True),
        'userstory': fields.integer('User Story', readonly=True,
                                    help='User history id of user history\
                                     assigned on task.'),
        'task_user_id': fields.many2one('res.users', 'Task user',
                                        readonly=True, select=True, help='User\
                                         of project task.'),
        'project_leader_id': fields.many2one('res.users', 'Leader user',
                                             readonly=True, select=True,
                                             help='Leader user of project\
                                                 task.'),
        'task_id': fields.many2one('project.task', 'Task',
                                   readonly=True, select=True, help='Project\
                                    task title.'),
        'deadline': fields.date('Deadline', readonly=True,
                                help='Project task deadline.'),
        'date_end': fields.date('Date End', readonly=True,
                                help='Project task Date End.'),
        'period_end': fields.char('Period End', 128,
                                  help='Period for the end date of summary\
                                   work.'),
        'state': fields.char('State', 128, help='Project task state.'),
    }

    def init(self, cr):
        '''
        Search method that executes query.
        '''
        drop_view_if_exists(cr, 'custom_project_task')
        cr.execute('''
            create or replace view custom_project_task as (
                SELECT
                    1 AS counter,
                    task.id AS id,
                    task.date_deadline AS deadline,
                    task.user_id AS task_user_id,
                    task.project_leader_id AS project_leader_id,
                    date(task.date_end) AS date_end,
                    to_char(task.date_end,'MM/YYYY') AS period_end,
                    analytic.id AS analytic_id,
                    us.id AS userstory,
                    task.id AS task_id,
                    task_type.name AS state
                FROM project_task AS task
                LEFT JOIN project_project AS project ON project.id = task.project_id
                LEFT JOIN account_analytic_account AS analytic ON analytic.id = project.analytic_account_id
                LEFT JOIN user_story AS us ON us.id = task.userstory_id
                LEFT JOIN project_task_type AS task_type ON task_type.id = task.stage_id
        )''')
