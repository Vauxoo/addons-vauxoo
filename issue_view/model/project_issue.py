#-*- coding: utf-8 -*-
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
        'task_id': fields.many2one('project.task', 'Task', domain="[('project_id','=',project_id)]"),
        'product_backlog_id': fields.related('task_id', 'product_backlog_id', relation='project.scrum.product.backlog', type='many2one', string='Backlog', store=True),
        'sprint_id': fields.related('task_id', 'sprint_id', relation='project.scrum.sprint', type='many2one', string='Sprint', store=True),
        'planned_hours': fields.related('task_id', 'planned_hours', type='float', string='Horas', store=False),
    }
