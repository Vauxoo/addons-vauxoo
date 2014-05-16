# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Luis Ernesto García Medina (ernesto_gm@vauxoo.com)
#
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

from openerp.osv import osv, fields


class project(osv.Model):
    _inherit = 'project.project'

    def _get_followers(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for project in self.browse(cr, uid, ids, context=context):
            task_ids = self.pool.get('project.task').search(
                cr, uid, [('project_id', '=', project.id)])
            for task in self.pool.get('project.task').browse(cr, uid, task_ids):
                if task.message_follower_ids:
                    result[project.id] = [
                        follower.id for follower in task.message_follower_ids]
        return result

    def _search_project(self, cr, uid, obj, name, args, context):
        for cond in args:
            partner_ids = cond[2]
            task_ids = self.pool.get('project.task').search(
                cr, uid, [('message_follower_ids', 'in', partner_ids), 
                    ('project_id.privacy_visibility', '=', 'followers')])
        project_ids = set(task.project_id.id for task in self.pool.get(
            'project.task').browse(cr, uid, task_ids))
        return [('id', 'in', tuple(project_ids))]
    _columns = {
        'followers_tasks_ids': fields.function(_get_followers, type='many2many', 
            relation="res.partner", string="Followers Task", method=True, store=False, 
                fnct_search=_search_project),
    }
