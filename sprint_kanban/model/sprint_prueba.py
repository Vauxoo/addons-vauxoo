# -*- coding: utf-8 -*-

import time
from lxml import etree
from datetime import datetime, date

import tools
from base_status.base_stage import base_stage
from osv import fields, osv
from openerp.addons.resource.faces import task as Task
from tools.translate import _
from openerp import SUPERUSER_ID

_TASK_STATE = [('draft', 'New'),('open', 'In Progress'),('pending', 'Pending'), ('done', 'Done'), ('cancelled', 'Cancelled')]



class project(osv.osv):
	
    _name = "sprint.sprint"
    _description = "Sprint"
    _inherits = {'account.analytic.account': "analytic_account_id",
                 "mail.alias": "alias_id","project.task.type":"name"}
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        if user == 1:
            return super(project, self).search(cr, user, args, offset=offset, limit=limit, order=order, context=context, count=count)
        if context and context.get('user_preference'):
                cr.execute("""SELECT project.id FROM project_project project
                           LEFT JOIN account_analytic_account account ON account.id = project.analytic_account_id
                           LEFT JOIN project_user_rel rel ON rel.project_id = project.analytic_account_id
                           WHERE (account.user_id = %s or rel.uid = %s)"""%(user, user))
                return [(r[0]) for r in cr.fetchall()]
        return super(project, self).search(cr, user, args, offset=offset, limit=limit, order=order,
            context=context, count=count)
	
	
        
    #~ def _complete_name(self, cr, uid, ids, name, args, context=None):
        #~ res = {}
        #~ for m in self.browse(cr, uid, ids, context=context):
            #~ res[m.id] = (m.parent_id and (m.parent_id.name + '/') or '') + m.name
        #~ return res

    def onchange_partner_id(self, cr, uid, ids, part=False, context=None):
        partner_obj = self.pool.get('res.partner')
        if not part:
            return {'value':{}}
        val = {}
        if 'pricelist_id' in self.fields_get(cr, uid, context=context):
            pricelist = partner_obj.read(cr, uid, part, ['property_product_pricelist'], context=context)
            pricelist_id = pricelist.get('property_product_pricelist', False) and pricelist.get('property_product_pricelist')[0] or False
            val['pricelist_id'] = pricelist_id
        return {'value': val}

    def _get_projects_from_tasks(self, cr, uid, task_ids, context=None):
        tasks = self.pool.get('project.task').browse(cr, uid, task_ids, context=context)
        project_ids = [task.project_id.id for task in tasks if task.project_id]
        return self.pool.get('sprint.sprint')._get_project_and_parents(cr, uid, project_ids, context)

    def _get_project_and_parents(self, cr, uid, ids, context=None):
        """ return the project ids and all their parent projects """
        res = set(ids)
        while ids:
            cr.execute("""
                SELECT DISTINCT parent.id
                FROM project_project project, project_project parent, account_analytic_account account
                WHERE project.analytic_account_id = account.id
                AND parent.analytic_account_id = account.parent_id
                AND project.id IN %s
                """, (tuple(ids),))
            ids = [t[0] for t in cr.fetchall()]
            res.update(ids)
        return list(res)

    def _get_project_and_children(self, cr, uid, ids, context=None):
        """ retrieve all children projects of project ids;
            return a dictionary mapping each project to its parent project (or None)
        """
        res = dict.fromkeys(ids, None)
        while ids:
            cr.execute("""
                SELECT project.id, parent.id
                FROM project_project project, project_project parent, account_analytic_account account
                WHERE project.analytic_account_id = account.id
                AND parent.analytic_account_id = account.parent_id
                AND parent.id IN %s
                """, (tuple(ids),))
            dic = dict(cr.fetchall())
            res.update(dic)
            ids = dic.keys()
        return res

    def _progress_rate(self, cr, uid, ids, names, arg, context=None):
        child_parent = self._get_project_and_children(cr, uid, ids, context)
        # compute planned_hours, total_hours, effective_hours specific to each project
        cr.execute("""
            SELECT project_id, COALESCE(SUM(planned_hours), 0.0),
                COALESCE(SUM(total_hours), 0.0), COALESCE(SUM(effective_hours), 0.0)
            FROM project_task WHERE project_id IN %s AND state <> 'cancelled'
            GROUP BY project_id
            """, (tuple(child_parent.keys()),))
        # aggregate results into res
        res = dict([(id, {'planned_hours':0.0,'total_hours':0.0,'effective_hours':0.0}) for id in ids])
        for id, planned, total, effective in cr.fetchall():
            # add the values specific to id to all parent projects of id in the result
            while id:
                if id in ids:
                    res[id]['planned_hours'] += planned
                    res[id]['total_hours'] += total
                    res[id]['effective_hours'] += effective
                id = child_parent[id]
        # compute progress rates
        for id in ids:
            if res[id]['total_hours']:
                res[id]['progress_rate'] = round(100.0 * res[id]['effective_hours'] / res[id]['total_hours'], 2)
            else:
                res[id]['progress_rate'] = 0.0
        return res

    def unlink(self, cr, uid, ids, *args, **kwargs):
        alias_ids = []
        mail_alias = self.pool.get('mail.alias')
        for proj in self.browse(cr, uid, ids):
            if proj.tasks:
                raise osv.except_osv(_('Invalid Action!'),
                                     _('You cannot delete a project containing tasks. You can either delete all the project\'s tasks and then delete the project or simply deactivate the project.'))
            elif proj.alias_id:
                alias_ids.append(proj.alias_id.id)
        res =  super(project, self).unlink(cr, uid, ids, *args, **kwargs)
        mail_alias.unlink(cr, uid, alias_ids, *args, **kwargs)
        return res

    def _task_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0)
        task_ids = self.pool.get('project.task').search(cr, uid, [('project_id', 'in', ids)])
        for task in self.pool.get('project.task').browse(cr, uid, task_ids, context):
            res[task.project_id.id] += 1
        return res

    def _get_alias_models(self, cr, uid, context=None):
        """Overriden in project_issue to offer more options"""
        return [('project.task', "Tasks")]

    # Lambda indirection method to avoid passing a copy of the overridable method when declaring the field
    _alias_models = lambda self, *args, **kwargs: self._get_alias_models(*args, **kwargs)
    _columns = {
        'name_sprint': fields.char('Name Sprint',264, required=True),
        'project_id': fields.many2one('project.project','Project',ondelete="cascade"),
	    'description': fields.text('Description'),
        #~ 'complete_name': fields.function(_complete_name, string="Project Name", type='char', size=250),
        'active': fields.boolean('Active', help="If the active field is set to False, it will allow you to hide the project without removing it."),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of Projects."),
        'priority': fields.integer('Sequence', help="Gives the sequence order when displaying the list of projects"),
        'members': fields.many2many('res.users', 'project_user_rel', 'project_id', 'uid', 'Project Members',
            help="Project's members are users who can have an access to the tasks related to this project.", states={'close':[('readonly',True)], 'cancelled':[('readonly',True)]}),
        'tasks': fields.one2many('project.task', 'project_id', "Task Activities"),
        'planned_hours': fields.function(_progress_rate, multi="progress", string='Planned Time', help="Sum of planned hours of all tasks related to this project and its child projects.",
            store = {
                'sprint.sprint': (_get_project_and_parents, ['tasks', 'parent_id', 'child_ids'], 10),
                'project.task': (_get_projects_from_tasks, ['planned_hours', 'remaining_hours', 'work_ids', 'state'], 20),
            }),
        'effective_hours': fields.function(_progress_rate, multi="progress", string='Time Spent', help="Sum of spent hours of all tasks related to this project and its child projects.",
            store = {
                'sprint.sprint': (_get_project_and_parents, ['tasks', 'parent_id', 'child_ids'], 10),
                'project.task': (_get_projects_from_tasks, ['planned_hours', 'remaining_hours', 'work_ids', 'state'], 20),
            }),
        'total_hours': fields.function(_progress_rate, multi="progress", string='Total Time', help="Sum of total hours of all tasks related to this project and its child projects.",
            store = {
                'sprint.sprint': (_get_project_and_parents, ['tasks', 'parent_id', 'child_ids'], 10),
                'project.task': (_get_projects_from_tasks, ['planned_hours', 'remaining_hours', 'work_ids', 'state'], 20),
            }),
        'progress_rate': fields.function(_progress_rate, multi="progress", string='Progress', type='float', group_operator="avg", help="Percent of tasks closed according to the total of tasks todo.",
            store = {
                'sprint.sprint': (_get_project_and_parents, ['tasks', 'parent_id', 'child_ids'], 10),
                'project.task': (_get_projects_from_tasks, ['planned_hours', 'remaining_hours', 'work_ids', 'state'], 20),
            }),
        'resource_calendar_id': fields.many2one('resource.calendar', 'Working Time', help="Timetable working hours to adjust the gantt diagram report", states={'close':[('readonly',True)]} ),
        'type_ids': fields.many2many('project.task.type', 'project_task_type_rel', 'project_id', 'type_id', 'Tasks Stages', states={'close':[('readonly',True)], 'cancelled':[('readonly',True)]}),
        'task_count': fields.function(_task_count, type='integer', string="Open Tasks"),
        'color': fields.integer('Color Index'),
        'alias_id': fields.many2one('mail.alias', 'Alias', ondelete="cascade", required=True,
                                    help="Internal email associated with this project. Incoming emails are automatically synchronized"
                                         "with Tasks (or optionally Issues if the Issue Tracker module is installed)."),
        'alias_model': fields.selection(_alias_models, "Alias Model", select=True, required=True,
                                        help="The kind of document created when an email is received on this project's email alias"),
        #~ 'privacy_visibility': fields.selection([('public','Public'), ('followers','Followers Only')], 'Privacy / Visibility', required=True),
        'state': fields.selection([('template', 'Template'),('draft','New'),('open','In Progress'), ('cancelled', 'Cancelled'),('pending','Pending'),('close','Closed')], 'Status', required=True,),
     }

    def _get_type_common(self, cr, uid, context):
        ids = self.pool.get('project.task.type').search(cr, uid, [('case_default','=',1)], context=context)
        return ids

    _order = "sequence"
    _defaults = {
        'active': True,
        'type': 'contract',
        'state': 'open',
        'priority': 1,
        'sequence': 10,
        'type_ids': _get_type_common,
        'alias_model': 'project.task',
        #~ 'privacy_visibility': 'public',
        'alias_domain': False, # always hide alias during creation
    }

    # TODO: Why not using a SQL contraints ?
    def _check_dates(self, cr, uid, ids, context=None):
        for leave in self.read(cr, uid, ids, ['date_start', 'date'], context=context):
            if leave['date_start'] and leave['date']:
                if leave['date_start'] > leave['date']:
                    return False
        return True

    _constraints = [
        (_check_dates, 'Error! project start-date must be lower then project end-date.', ['date_start', 'date'])
    ]

    #~ def set_template(self, cr, uid, ids, context=None):
        #~ res = self.setActive(cr, uid, ids, value=False, context=context)
        #~ return res

    def set_done(self, cr, uid, ids, context=None):
        task_obj = self.pool.get('project.task')
        task_ids = task_obj.search(cr, uid, [('project_id', 'in', ids), ('state', 'not in', ('cancelled', 'done'))])
        task_obj.case_close(cr, uid, task_ids, context=context)
        self.write(cr, uid, ids, {'state':'close'}, context=context)
        self.set_close_send_note(cr, uid, ids, context=context)
        return True

    def set_cancel(self, cr, uid, ids, context=None):
        task_obj = self.pool.get('project.task')
        task_ids = task_obj.search(cr, uid, [('project_id', 'in', ids), ('state', '!=', 'done')])
        task_obj.case_cancel(cr, uid, task_ids, context=context)
        self.write(cr, uid, ids, {'state':'cancelled'}, context=context)
        self.set_cancel_send_note(cr, uid, ids, context=context)
        return True

    def set_pending(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'pending'}, context=context)
        self.set_pending_send_note(cr, uid, ids, context=context)
        return True

    def set_open(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'open'}, context=context)
        self.set_open_send_note(cr, uid, ids, context=context)
        return True

    def reset_project(self, cr, uid, ids, context=None):
        res = self.setActive(cr, uid, ids, value=True, context=context)
        self.set_open_send_note(cr, uid, ids, context=context)
        return res

    def map_tasks(self, cr, uid, old_project_id, new_project_id, context=None):
        """ copy and map tasks from old to new project """
        if context is None:
            context = {}
        map_task_id = {}
        task_obj = self.pool.get('project.task')
        proj = self.browse(cr, uid, old_project_id, context=context)
        for task in proj.tasks:
            map_task_id[task.id] =  task_obj.copy(cr, uid, task.id, {}, context=context)
        self.write(cr, uid, [new_project_id], {'tasks':[(6,0, map_task_id.values())]})
        task_obj.duplicate_task(cr, uid, map_task_id, context=context)
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        if default is None:
            default = {}

        context['active_test'] = False
        default['state'] = 'open'
        default['tasks'] = []
        default.pop('alias_name', None)
        default.pop('alias_id', None)
        proj = self.browse(cr, uid, id, context=context)
        if not default.get('name', False):
            default.update(name=_("%s (copy)") % (proj.name))
        res = super(project, self).copy(cr, uid, id, default, context)
        self.map_tasks(cr,uid,id,res,context)
        return res


        if result and len(result):
            res_id = result[0]
            form_view_id = data_obj._get_id(cr, uid, 'project', 'edit_project')
            form_view = data_obj.read(cr, uid, form_view_id, ['res_id'])
            tree_view_id = data_obj._get_id(cr, uid, 'project', 'view_project')
            tree_view = data_obj.read(cr, uid, tree_view_id, ['res_id'])
            search_view_id = data_obj._get_id(cr, uid, 'project', 'view_project_project_filter')
            search_view = data_obj.read(cr, uid, search_view_id, ['res_id'])
            return {
                'name': _('Projects'),
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'sprint.sprint',
                'view_id': False,
                'res_id': res_id,
                'views': [(form_view['res_id'],'form'),(tree_view['res_id'],'tree')],
                'type': 'ir.actions.act_window',
                'search_view_id': search_view['res_id'],
                'nodestroy': True
            }

    # set active value for a project, its sub projects and its tasks
    def setActive(self, cr, uid, ids, value=True, context=None):
        task_obj = self.pool.get('project.task')
        for proj in self.browse(cr, uid, ids, context=None):
            self.write(cr, uid, [proj.id], {'state': value and 'open' or 'template'}, context)
            cr.execute('select id from project_task where project_id=%s', (proj.id,))
            tasks_id = [x[0] for x in cr.fetchall()]
            if tasks_id:
                task_obj.write(cr, uid, tasks_id, {'active': value}, context=context)
            child_ids = self.search(cr, uid, [('parent_id','=', proj.analytic_account_id.id)])
            if child_ids:
                self.setActive(cr, uid, child_ids, value, context=None)
        return True

    def _schedule_header(self, cr, uid, ids, force_members=True, context=None):
        context = context or {}
        if type(ids) in (long, int,):
            ids = [ids]
        projects = self.browse(cr, uid, ids, context=context)

        for project in projects:
            if (not project.members) and force_members:
                raise osv.except_osv(_('Warning!'),_("You must assign members on the project '%s' !") % (project.name,))

        resource_pool = self.pool.get('resource.resource')

        result = "from openerp.addons.resource.faces import *\n"
        result += "import datetime\n"
        for project in self.browse(cr, uid, ids, context=context):
            u_ids = [i.id for i in project.members]
            if project.user_id and (project.user_id.id not in u_ids):
                u_ids.append(project.user_id.id)
            for task in project.tasks:
                if task.state in ('done','cancelled'):
                    continue
                if task.user_id and (task.user_id.id not in u_ids):
                    u_ids.append(task.user_id.id)
            calendar_id = project.resource_calendar_id and project.resource_calendar_id.id or False
            resource_objs = resource_pool.generate_resources(cr, uid, u_ids, calendar_id, context=context)
            for key, vals in resource_objs.items():
                result +='''
class User_%s(Resource):
    efficiency = %s
''' % (key,  vals.get('efficiency', False))

        result += '''
def Project():
        '''
        return result

    def _schedule_project(self, cr, uid, project, context=None):
        resource_pool = self.pool.get('resource.resource')
        calendar_id = project.resource_calendar_id and project.resource_calendar_id.id or False
        working_days = resource_pool.compute_working_calendar(cr, uid, calendar_id, context=context)
        # TODO: check if we need working_..., default values are ok.
        puids = [x.id for x in project.members]
        if project.user_id:
            puids.append(project.user_id.id)
        result = """
  def Project_%d():
    start = \'%s\'
    working_days = %s
    resource = %s
"""       % (
            project.id,
            project.date_start, working_days,
            '|'.join(['User_'+str(x) for x in puids])
        )
        vacation = calendar_id and tuple(resource_pool.compute_vacation(cr, uid, calendar_id, context=context)) or False
        if vacation:
            result+= """
    vacation = %s
""" %   ( vacation, )
        return result

    #TODO: DO Resource allocation and compute availability
    def compute_allocation(self, rc, uid, ids, start_date, end_date, context=None):
        if context ==  None:
            context = {}
        allocation = {}
        return allocation

    def schedule_tasks(self, cr, uid, ids, context=None):
        context = context or {}
        if type(ids) in (long, int,):
            ids = [ids]
        projects = self.browse(cr, uid, ids, context=context)
        result = self._schedule_header(cr, uid, ids, False, context=context)
        for project in projects:
            result += self._schedule_project(cr, uid, project, context=context)
            result += self.pool.get('project.task')._generate_task(cr, uid, project.tasks, ident=4, context=context)

        local_dict = {}
        exec result in local_dict
        projects_gantt = Task.BalancedProject(local_dict['Project'])

        for project in projects:
            project_gantt = getattr(projects_gantt, 'Project_%d' % (project.id,))
            for task in project.tasks:
                if task.state in ('done','cancelled'):
                    continue

                p = getattr(project_gantt, 'Task_%d' % (task.id,))

                self.pool.get('project.task').write(cr, uid, [task.id], {
                    'date_start': p.start.strftime('%Y-%m-%d %H:%M:%S'),
                    'date_end': p.end.strftime('%Y-%m-%d %H:%M:%S')
                }, context=context)
                if (not task.user_id) and (p.booked_resource):
                    self.pool.get('project.task').write(cr, uid, [task.id], {
                        'user_id': int(p.booked_resource[0].name[5:]),
                    }, context=context)
        return True

    # ------------------------------------------------
    # OpenChatter methods and notifications
    # ------------------------------------------------

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        # Prevent double project creation when 'use_tasks' is checked!
        context = dict(context, project_creation_in_progress=True)
        mail_alias = self.pool.get('mail.alias')
        if not vals.get('alias_id'):
            vals.pop('alias_name', None) # prevent errors during copy()
            alias_id = mail_alias.create_unique_alias(cr, uid,
                          # Using '+' allows using subaddressing for those who don't
                          # have a catchall domain setup.
                          {'alias_name': "project+"+short_name(vals['name'])},
                          model_name=vals.get('alias_model', 'project.task'),
                          context=context)
            vals['alias_id'] = alias_id
        vals['type'] = 'contract'
        project_id = super(project, self).create(cr, uid, vals, context)
        mail_alias.write(cr, uid, [vals['alias_id']], {'alias_defaults': {'project_id': project_id} }, context)
        self.create_send_note(cr, uid, [project_id], context=context)
        return project_id

    def create_send_note(self, cr, uid, ids, context=None):
        return self.message_post(cr, uid, ids, body=_("Project has been <b>created</b>."), context=context)

    def set_open_send_note(self, cr, uid, ids, context=None):
        return self.message_post(cr, uid, ids, body=_("Project has been <b>opened</b>."), context=context)

    def set_pending_send_note(self, cr, uid, ids, context=None):
        return self.message_post(cr, uid, ids, body=_("Project is now <b>pending</b>."), context=context)

    def set_cancel_send_note(self, cr, uid, ids, context=None):
        return self.message_post(cr, uid, ids, body=_("Project has been <b>canceled</b>."), context=context)

    def set_close_send_note(self, cr, uid, ids, context=None):
        return self.message_post(cr, uid, ids, body=_("Project has been <b>closed</b>."), context=context)

    def write(self, cr, uid, ids, vals, context=None):
        # if alias_model has been changed, update alias_model_id accordingly
        if vals.get('alias_model'):
            model_ids = self.pool.get('ir.model').search(cr, uid, [('model', '=', vals.get('alias_model', 'project.task'))])
            vals.update(alias_model_id=model_ids[0])
        return super(project, self).write(cr, uid, ids, vals, context=context)


class sprint_kanban_tasks(osv.osv):

    _inherit = 'project.task'
    
    _columns={
	 
	    'sprint_id':fields.many2one('sprint.kanban','Sprint',ondelete="cascade"),
	 		
 }
sprint_kanban_tasks()

class sprint_kanban_h(osv.osv):

    _inherit = 'project.task.history.cumulative'
    
    _columns={
	 
	    #~ 'sprint_id':fields.many2one('sprint.kanban','Sprint',ondelete="cascade"),
	 		
 }
sprint_kanban_tasks()




