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

from openerp.osv import fields, osv
from openerp.tools.translate import _

import time

_US_STATE = [('draft', 'New'), ('open', 'In Progress'), (
    'pending', 'Pending'), ('done', 'Done'), ('cancelled', 'Cancelled')]


class user_story(osv.Model):
    """
    OpenERP Model : User Story
    """

    _name = 'user.story'
    _inherit = ['mail.thread']

    def _get_tasks(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        task_obj = self.pool.get('project.task')
        for orderpoint in self.browse(cr, uid, ids, context=context):
            task_ids = task_obj.search(cr, uid, [
                                       ('userstory_id', '=', orderpoint.id)])
            result[orderpoint.id] = task_ids
        return result

    def _set_task(self, cr, uid, id, name, value, arg, ctx=None):

        task_ids = self.pool.get('project.task').search(
            cr, uid, [("userstory_id", '=', id)])
        task_id = list(set(value[0][2]) - set(task_ids))
        if task_id:
            for i in task_id:
                sql_str = """UPDATE project_task set
                            userstory_id='%s'
                            WHERE id=%s """ % (id, i)
                cr.execute(sql_str)
        else:
            task_id = list(set(task_ids) - set(value[0][2]))
            for i in task_id:
                    sql_str = """UPDATE project_task set
                                userstory_id=Null
                                WHERE id=%s """ % (i)
                    cr.execute(sql_str)
        return True

    def write(self, cr, uid, ids, vals, context=None):
        task_obj = self.pool.get('project.task')
        
        if vals.get('categ_ids'):
            for tag_id in self.browse(cr, uid, ids, context=context):
                for task in tag_id.task_ids:
                    task_obj.write(cr, uid, [task.id], {'categ_ids': vals['categ_ids']})
                   
        if vals.get('sk_id'):
            task_ids = task_obj.search(cr, uid, [
                                       ('userstory_id', '=', ids[0])])
            task_obj.write(cr, uid, task_ids, {
                           'sprint_id': vals.get('sk_id')}, context=context)
        return super(user_story, self).write(cr, uid, ids,
                                             vals, context=context)
        
     
    _columns = {
        'name': fields.char('Title', size=255, required=True, readonly=False,
            translate=True),
        'owner': fields.char('Owner', size=255, required=True, readonly=False),
        'code': fields.char('Code', size=64, readonly=False),
        'planned_hours': fields.float('Planned Hours'),
        'project_id': fields.many2one('project.project', 'Project',
                                      required=True),
        'description': fields.text('Description', translate=True),
        'accep_crit_ids': fields.one2many('acceptability.criteria',
                                          'accep_crit_id',
                                          'Acceptability Criteria',
                                          required=False),
        'info': fields.text('Other Info', translate=True),
        'priority_level':fields.many2one(
            'user.story.priority',
            'Priority Level',
            help=('User story level priority, used to define priority for'
                  ' each user story')), 
        'asumption': fields.text('Asumptions', translate=True),
        'date': fields.date('Date'),
        'user_id': fields.many2one('res.users', 'Responsible Supervisor',help="Person responsible for interacting with the client to give details of the progress or completion of the User History, in some cases also the supervisor for the correct execution of the user story."),
        'user_execute_id': fields.many2one('res.users', 'Responsible Execution',help="Person responsible for user story takes place, either by delegating work to other human capital or running it by itself. For delegate work should monitor the proper implementation of associated activities."),
        'sk_id': fields.many2one('sprint.kanban', 'Sprint Kanban'),
        'state': fields.selection(_US_STATE, 'State', readonly=True),
        'task_ids': fields.function(_get_tasks, type='many2many',
                                    relation="project.task",
                                    fnct_inv=_set_task,
                                    string="Tasks",
                                    help="""Draft procurement of
                                            the product and location
                                            of that orderpoint"""),
        'categ_ids': fields.many2many('project.category','project_category_user_story_rel','userstory_id','categ_id', string="Tags"),
        'implementation': fields.text('Implementation Conclusions', translate=True),
    }
    _defaults = {
        'name': lambda *a: None,
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'user_id': lambda self, cr, uid, ctx: uid,
        'user_execute_id': lambda self, cr, uid, ctx: uid,
        'state': 'draft',
        'priority_level': lambda self, cr, uid, ctx: self.pool.get(
            'user.story.priority').search(
                cr, uid, [('name', 'like', 'Secondary')], context=ctx)[0]
    }

    def do_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def do_progress(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'open'}, context=context)

    def do_pending(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'pending'}, context=context)

    def do_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)

    def do_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancelled'},
                          context=context)

class user_story_priority(osv.Model):
    """
    User Story Priority Level
    """

    _name = 'user.story.priority'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
    }


class acceptability_criteria(osv.Model):
    """
    OpenERP Model : Acceptability Criteria
    """

    _name = 'acceptability.criteria'

    def _get_ac_ids_by_us_ids(self, cr, uid, us_ids, context=None):
        """
        This method is as the method of the sensitive store tuple for the
        functional fields defined in the current field that pretend to pull
        data form the user.story model. The method get us_ids and make a search
        for the acceptability.criteria records that need to be updated.
        @return a list of the acceptability.criteria that need to be updated.
        """
        context = context or {}
        us_obj = self.pool.get('user.story')
        ac_obj = self.pool.get('acceptability.criteria')
        ac_ids = ac_obj.search(
            cr, uid, [('accep_crit_id', 'in', us_ids)], context=context)
        return ac_ids

    def _get_user_story_field(self, cr, uid, ids, fieldname, arg, context=None):
        """
        Method used as the function for extracting values for the user.story
        model using functional fields. This method is used for various fields,
        the fieldname it matters to extract the value, the field name need to
        be the same from the user.story model.
        """
        context = context or {}
        res = {}.fromkeys(ids)
        for ac_brw in self.browse(cr, uid, ids, context=context):
            res[ac_brw.id] = \
                getattr(ac_brw.accep_crit_id, fieldname, False) and \
                getattr(ac_brw.accep_crit_id, fieldname).id or False
        return res

    _columns = {
        'name': fields.char('Title', size=255, required=True, readonly=False,
            translate=True),
        'scenario': fields.text('Scenario', required=True, translate=True),
        'accep_crit_id': fields.many2one('user.story',
                                         'User Story',
                                         required=True),
        'accepted': fields.boolean('Accepted',
                                   help='Chek if this criteria apply'),
        'development': fields.boolean('Development'),
        'difficulty': fields.selection(
            [('low','Low'),
             ('medium','Medium'),
             ('high','High'),
             ('na','Not Apply')],
            string='Difficulty'),
        'project_id': fields.function(
            _get_user_story_field,
            type="many2one",
            relation='project.project',
            string='Project',
            help='User Story Project',
            store={
                'acceptability.criteria': (lambda s, c, u, i, ctx: i, ['accep_crit_id'], 16),
                'user.story': (_get_ac_ids_by_us_ids, ['project_id'], 20),
            }),
        'sk_id': fields.function(
            _get_user_story_field,
            type="many2one",
            relation="sprint.kanban",
            string='Sprint',
            help='Sprint Kanban',
            store={
                'acceptability.criteria': (lambda s, c, u, i, ctx: i, ['accep_crit_id'], 16),
                'user.story': (_get_ac_ids_by_us_ids, ['sk_id'], 20),
            }),
        'tag': fields.related('accep_crit_id', 'categ_ids',
                                     relation="project.category",
                                     type="many2one", string='Tag',
                                     help='User Story Category',
                                     readonly=True,
                                     store=True),
        'user_id': fields.related('accep_crit_id', 'user_id',
                                     relation="res.users",
                                     type="many2one", string='Responsible Supervisor',
                                     help='User Story Supervisor',
                                     readonly=True,
                                     store=True),
        'user_execute_id': fields.related('accep_crit_id', 'user_execute_id',
                                     relation="res.users",
                                     type="many2one", string='Responsible Execution',
                                     help='User Story Responsible Execution',
                                     readonly=True,
                                     store=True),
    }
    _defaults = {
        'name': lambda *a: None,
        'difficulty': 'na',
    }


class project_task(osv.Model):
    """
    OpenERP Model : Project Task
    """
    _inherit = 'project.task'

    def default_get(self, cr, uid, fields, context=None):
        '''Owerwrite default get to add project in new task automatically'''
        if context is None:
            context = {}
        res = super(project_task, self).default_get(cr, uid, fields, context=context)
        context.get('project_task',False) and \
                res.update({'project_id':context.get('project_task'),'categ_ids':context.get('categ_task'),
                            'sprint_id':context.get('sprint_task'),'userstory_id':context.get('userstory_task')})
        return res
    

    def onchange_user_story_task(self, cr, uid, ids, us_id, context=None):
        v = {}
        us_obj = self.pool.get('user.story')
        if us_id:
            sprint = us_obj.browse(cr, uid, us_id, context=context)
            if sprint.sk_id:
                v['sprint_id'] = sprint.sk_id.id
            categs = us_obj.browse(cr, uid, us_id, context=context)
            if categs.categ_ids:
                v['categ_ids'] = [cat.id for cat in categs.categ_ids]
        return {'value': v}

    _columns = {
        'userstory_id': fields.many2one('user.story', 'User Story',
                                        #domain="[('sk_id', '=', sprint_id)]",
                                        help="Set here the User Story related with this task"),
        'branch_to_clone':fields.char('Branch to clone', 512,
                                      help='Branch source for clone and'
                                           ' make merge proposal'), 
        
    }
class inherit_project(osv.Model):
    
    '''Inheirt project model to a new Descripcion field'''
    
    _inherit = 'project.project'

    _columns = {
            'descriptions':fields.text('Description',
                                       help="reference on what the project "
                                            "is about"),
            }
