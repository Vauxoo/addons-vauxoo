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

from openerp.osv import osv, fields


class project_issue(osv.Model):

    _inherit = 'project.issue'

    _columns = {
        'analytic_account_id': fields.many2one('account.analytic.account',
                                               'Analytic Account',
                                                track_visibility='onchange',
                                                help='Analytic account to '
                                                     'load the work in '
                                                     'case you want set '
                                                     'timesheet on the task'
                                                     ' related to this issue.'),
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
        # Setting task
        for i in ids:
            issue = self.browse(cr, uid, i, context=context)
            if issue.task_id and issue.analytic_account_id:
                context.update({'analytic_account_id':
                                issue.analytic_account_id.id})
                issue.task_id.write({
                    'project_id': self._get_project_id(cr, uid, ids,
                                                       context=context)})
                for t in issue.timesheet_ids:
                    t.write({'account_id': issue.analytic_account_id.id})

            else:
                raise osv.except_osv(
                    'Error!',
                    'In order to be consistent, you must set a task and an '
                    'analytic account to be consistent on this action.')
        return True
