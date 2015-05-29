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
        'analytic_account_id': fields.many2one('project.project',
                                               'Analytic Account',
                                               help='Project to load '
                                               'the work in case you '
                                               'want set timesheet on the task'
                                               ' related to this issue.')
    }

    def take_for_me(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'user_id': uid}, context=context)
        return True

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
