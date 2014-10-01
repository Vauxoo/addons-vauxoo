#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: julio (julio@vauxoo.com)
#    Modify by: carlos(juan@vauxoo.com)
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################
from osv import osv


class project_task(osv.osv):
    _inherit = 'project.task'

    def write(self, cr, uid, ids, vals, context=None):
        res = super(project_task, self).write(cr, uid, ids, vals, context)
        try:
            issue_obj = self.pool.get('project.issue')
            issue_ids = issue_obj.search(cr, uid, [(
                'task_id', 'in', [ids])], context=context)
            issue_datas = issue_obj.read(
                cr, uid, issue_ids, ['task_id'], context=context)
            for issue_data in issue_datas:
                issue_obj.write(cr, uid, issue_ids, {'task_id': False})
                issue_obj.write(cr, uid, issue_ids, {
                                'task_id': issue_data['task_id'][0]})
        except:
            pass
        return res
