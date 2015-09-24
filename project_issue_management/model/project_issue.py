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

from openerp.osv import osv, fields


class ProjectIssue(osv.Model):

    _inherit = 'project.issue'

    def _check_analytic_accounts(self, cr, uid, ids, args, fields,
                                 context=None):
        context = context or {}
        res = {}
        for issue in self.browse(cr, uid, ids, context=context):
            if issue.task_id and issue.task_id.project_id and \
                    issue.analytic_account_id:
                res[issue.id] = issue.analytic_account_id.id == \
                    issue.task_id.project_id.analytic_account_id.id
            else:
                res[issue.id] = False
        return res

    def _check_task(self, cr, uid, ids, args, fields, context=None):
        context = context or {}
        res = {}
        for issue in self.browse(cr, uid, ids, context=context):
            res[issue.id] = issue.task_id and True or False
        return res

    def _check_partner(self, cr, uid, ids, args, fields, context=None):
        context = context or {}
        res = {}
        for issue in self.browse(cr, uid, ids, context=context):
            partner = []
            if issue.partner_id and issue.analytic_account_id:
                a_partner = issue.analytic_account_id.partner_id.id
                parent = issue.partner_id.parent_id
                partner.append(issue.partner_id.id)
                while parent:
                    partner.append(parent.id)
                    parent = parent.parent_id
                res[issue.id] = a_partner in partner
            else:
                res[issue.id] = False
        return res

    def _get_issue_ids_from_task(self, cr, uid, ids, context=None):
        context = context or {}
        issue_ids = self.pool.get('project.issue').\
            search(cr, uid, [('task_id', 'in', ids)])
        return issue_ids

    _columns = {
        'analytic_account_id': fields.many2one('account.analytic.account',
                                               'Analytic Account',
                                               track_visibility='onchange',
                                               help='Analytic account to '
                                                    'load the work in '
                                                    'case you want set '
                                                    'timesheet on the task'
                                                    ' related to this issue.'),
        'same_analytic': fields.function(_check_analytic_accounts,
                                         type='boolean',
                                         string='Same Analytics',
                                         store={
                                             'project.issue':
                                             (lambda s, c, u, ids, cx={}: ids,
                                              ['analytic_account_id',
                                               'task_id'], 10),
                                             'project.task':
                                             (_get_issue_ids_from_task,
                                              ['project_id'], 10)

                                         },
                                         help='Determines if the issue and '
                                         'the task related in the issue has'
                                         ' the same analytic account'),
        'has_task': fields.function(_check_task,
                                    type='boolean',
                                    string='Task',
                                    store={
                                        'project.issue':
                                        (lambda s, c, u, ids, cx={}: ids,
                                         ['task_id'], 10)
                                    },
                                    help='Selected if the issue '
                                    'has a task set'),
        'verify_partner': fields.function(_check_partner,
                                          type='boolean',
                                          string='Analytic Partner',
                                          store={'project.issue':
                                                 (lambda s, c, u, ids, cx={}:
                                                  ids,
                                                  ['partner_id',
                                                   'analytic_account_id'],
                                                  10)},
                                          help='Checked if the partner is '
                                          'related to the analytic account '
                                          'in the issue'),
    }

    def take_for_me(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'user_id': uid}, context=context)
        return True

    def _get_project_id(self, cr, uid, ids, context=None):
        project_obj = self.pool.get('project.project')
        res = project_obj.search(cr, uid, [('analytic_account_id', '=',
                                            context.get('analytic_account_id'))])
        if not res:
            raise osv.except_osv(
                'Error!',
                'In order to be consistent, you must set an analytic account '
                'which belong to a project')
        return res and res[0] or False

    def update_project(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for i in ids:
            issue = self.browse(cr, uid, i, context=context)
            if issue.task_id and issue.analytic_account_id:
                issue.task_id.write({
                    'project_id': issue.analytic_account_id.id})
            else:
                raise osv.except_osv(
                    'Error!',
                    'In order to be consistent, you must set a task and an '
                    'analytic account to be consistent on this action.')
        return True


class ProjectTask(osv.Model):

    _inherit = 'project.task'

    def _check_issue(self, cr, uid, ids, args, fields, context=None):
        context = context or {}
        res = {}
        issue_obj = self.pool.get('project.issue')
        for task in self.browse(cr, uid, ids, context=context):
            issue_ids = issue_obj.search(cr, uid,
                                         [('task_id',  '=', task.id)])

            res[task.id] = issue_ids and issue_ids[0] or False
        return res

    def _get_task_ids_from_issue(self, cr, uid, ids, context=None):
        context = context or {}
        task_ids = []
        issue_ids = self.search(cr, uid,
                                [('task_id', '!=', False),
                                 ('id', 'in', ids)])
        for issue in self.browse(cr, uid, issue_ids):
            task_ids.append(issue.task_id.id)
        return task_ids

    _columns = {
        'issue_id': fields.function(_check_issue,
                                    type='many2one',
                                    relation='project.issue',
                                    string='Issue',
                                    store={'project.issue':
                                           (_get_task_ids_from_issue,
                                            ['task_id'], 10)},
                                    help='Issue where this task is related'),

    }
