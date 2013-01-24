##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    

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

from osv import osv
from osv import fields
from tools.translate import _
import time

_US_STATE = [('draft', 'New'),('open', 'In Progress'),('pending', 'Pending'), ('done', 'Done'), ('cancelled', 'Cancelled')]

class user_story(osv.osv):
    """
    OpenERP Model : User Story
    """

    _name = 'user.story'

    def _get_tasks(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        task_obj = self.pool.get('project.task')
        for orderpoint in self.browse(cr, uid, ids, context=context):
            task_ids = task_obj.search(cr, uid , [('userstory_id', '=', orderpoint.id)])
            result[orderpoint.id] = task_ids
        return result

    def _set_task(self, cr, uid, id, name, value, arg, ctx=None):
        
        task_ids = self.pool.get('project.task').search(cr, uid , [("userstory_id",'=',id)])
        task_id = list(set(value[0][2]) - set(task_ids))
        if task_id:
            for i in task_id:
                sql_str = """UPDATE project_task set
                            userstory_id='%s'
                            WHERE id=%s """ % (id,i)
                cr.execute(sql_str)
        else:
            task_id = list(set(task_ids) - set(value[0][2]))
            for i in task_id:
                    sql_str = """UPDATE project_task set
                                userstory_id=Null
                                WHERE id=%s """ % (i)
                    cr.execute(sql_str)
        return True

    _columns = {
        'name':fields.char('Title', size=255, required=True, readonly=False),
        'owner':fields.char('Owner', size=255, required=True, readonly=False),
        'code':fields.char('Code', size=64, readonly=False),
        'planned_hours': fields.float('Planned Hours'),
        'project_id':fields.many2one('project.project', 'Project', required=True),
        'description':fields.text('Description'),
        'accep_crit_ids':fields.one2many('acceptability.criteria', 'accep_crit_id', 'Acceptability Criteria', required=False),
        'info': fields.text('Other Info'),
        'asumption': fields.text('Asumptions'),
        'date': fields.date('Date'),
        'user_id':fields.many2one('res.users', 'Create User'),
        'sk_id':fields.many2one('sprint.kanban', 'Sprint Kanban'),
        'state': fields.selection(_US_STATE, 'State',readonly=True),
        'task_ids': fields.function(_get_tasks, type='many2many', relation="project.task", fnct_inv=_set_task, \
                                string="Tasksss",help="Draft procurement of the product and location of that orderpoint"),
    }
    _defaults = {
        'name': lambda *a: None,
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'user_id': lambda self,cr,uid,ctx: uid,
        'state':'draft',
    }

    
    def do_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'draft'}, context=context)

    def do_progress(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'open'}, context=context)
        
    def do_pending(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'pending'}, context=context)
        
    def do_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'done'}, context=context)
        
    def do_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancelled'}, context=context)

user_story()


class acceptability_criteria(osv.osv):
    """
    OpenERP Model : Acceptability Criteria
    """

    _name = 'acceptability.criteria'

    _columns = {
        'name':fields.char('Title', size=255, required=True, readonly=False),
        'scenario': fields.text('Scenario', required=True),
        'accep_crit_id':fields.many2one('user.story', 'User Story', required=True),

    }
    _defaults = {
        'name': lambda *a: None,
    }
acceptability_criteria()


class project_task(osv.osv):
    """
    OpenERP Model : Project Task
    """

    _inherit = 'project.task'

    _columns = {
        'userstory_id':fields.many2one('user.story', 'User Story',help="Set hear the User Story related with this task"),

    }
project_task()


