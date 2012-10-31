# -*- coding: utf-8 -*-

from osv import fields
from osv import osv
from tools.translate import _
import time
import random
from datetime import datetime

class sprint_kanban(osv.osv): #
	
	_name = 'sprint.kanban'
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_columns = {
	            'name': fields.char('Name Sprint',264, required=True),
	            'project_id': fields.many2one('project.project','Project',ondelete="cascade"),
	            'description': fields.text('Description'),
	            'datestart': fields.date('Start Date'),
	            'dateend': fields.date('End Date'),
	            'color': fields.integer('Color Index'),
	            'members': fields.many2many('res.users', 'project_user_rel', 'project_id', 'uid', 'Project Members',states={'close':[('readonly',True)], 'cancelled':[('readonly',True)]}),
				'priority': fields.selection([('4','Very Low'), ('3','Low'), ('2','Medium'), ('1','Important'), ('0','Very important')], 'Priority', select=True),
			    'sprint_state': fields.selection([('normal', 'Normal'),('blocked', 'Blocked'),('done', 'Ready To Pull')], 'Kanban State', readonly=True, required=False),
	            'state': fields.selection([('template', 'Template'),('draft','New'),('open','In Progress'), ('cancelled', 'Cancelled'),('pending','Pending'),('close','Closed')], 'Status', required=True,),
	            }
	            
def set_template(self, cr, uid, ids, context=None):
	
	res = self.setActive(cr, uid, ids, value=False, context=context)
	return res
    
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
	
def duplicate_template(self, cr, uid, ids, context=None):
	if context is None:
		context = {}
	data_obj = self.pool.get('ir.model.data')
	result = []
	for proj in self.browse(cr, uid, ids, context=context):
		parent_id = context.get('parent_id', False)
		context.update({'analytic_project_copy': True})
		new_date_start = time.strftime('%Y-%m-%d')
		new_date_end = False
		if proj.date_start and proj.date:
			start_date = date(*time.strptime(proj.date_start,'%Y-%m-%d')[:3])
			end_date = date(*time.strptime(proj.date,'%Y-%m-%d')[:3])
			new_date_end = (datetime(*time.strptime(new_date_start,'%Y-%m-%d')[:3])+(end_date-start_date)).strftime('%Y-%m-%d')
		context.update({'copy':True})
		new_id = self.copy(cr, uid, proj.id, default = {
								'name':_("%s (copy)") % (proj.name),
								'state':'open',
								'date_start':new_date_start,
								'date':new_date_end,
								'parent_id':parent_id}, context=context)
		result.append(new_id)

		child_ids = self.search(cr, uid, [('parent_id','=', proj.analytic_account_id.id)], context=context)
		parent_id = self.read(cr, uid, new_id, ['analytic_account_id'])['analytic_account_id'][0]
		if child_ids:
			self.duplicate_template(cr, uid, child_ids, context={'parent_id': parent_id})

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
			'res_model': 'project.project',
			'view_id': False,
			'res_id': res_id,
			'views': [(form_view['res_id'],'form'),(tree_view['res_id'],'tree')],
			'type': 'ir.actions.act_window',
			'search_view_id': search_view['res_id'],
			'nodestroy': True
		}	            
sprint_kanban()	

class sprint_kanban_tasks(osv.osv):

    _inherit = 'project.task'
    
    _columns={
	 
	    'sprint_id':fields.many2one('sprint.kanban','Sprint',ondelete="cascade"),
	 
		
		
 }
sprint_kanban_tasks()




#~ 
 #~ _columns = {
        #~ 'active': fields.function(_is_template, store=True, string='Not a Template Task', type='boolean', help="This field is computed automatically and have the same behavior than the boolean 'active' field: if the task is linked to a template or unactivated project, it will be hidden unless specifically asked."),
        #~ 'name': fields.char('Task Summary', size=128, required=True, select=True),
        #~ 'description': fields.text('Description'),
        #~ 'priority': fields.selection([('4','Very Low'), ('3','Low'), ('2','Medium'), ('1','Important'), ('0','Very important')], 'Priority', select=True),
        #~ 'sequence': fields.integer('Sequence', select=True, help="Gives the sequence order when displaying a list of tasks."),
        #~ 'stage_id': fields.many2one('project.task.type', 'Stage',
                        #~ domain="['&', ('fold', '=', False), '|', ('project_ids', '=', project_id), ('case_default', '=', True)]"),
        #~ 'state': fields.related('stage_id', 'state', type="selection", store=True,
                #~ selection=_TASK_STATE, string="Status", readonly=True,
                #~ help='The status is set to \'Draft\', when a case is created.\
                      #~ If the case is in progress the status is set to \'Open\'.\
                      #~ When the case is over, the status is set to \'Done\'.\
                      #~ If the case needs to be reviewed then the status is \
                      #~ set to \'Pending\'.'),
        #~ 'categ_ids': fields.many2many('project.category', string='Tags'),
        #~ 'kanban_state': fields.selection([('normal', 'Normal'),('blocked', 'Blocked'),('done', 'Ready To Pull')], 'Kanban State',
                                         #~ help="A task's kanban state indicates special situations affecting it:\n"
                                              #~ " * Normal is the default situation\n"
                                              #~ " * Blocked indicates something is preventing the progress of this task\n"
                                              #~ " * Ready To Pull indicates the task is ready to be pulled to the next stage",
                                         #~ readonly=True, required=False),
        #~ 'create_date': fields.datetime('Create Date', readonly=True,select=True),
        #~ 'date_start': fields.datetime('Starting Date',select=True),
        #~ 'date_end': fields.datetime('Ending Date',select=True),
        #~ 'date_deadline': fields.date('Deadline',select=True),
        #~ 'project_id': fields.many2one('project.project', 'Project', ondelete='set null', select="1"),
        #~ 'parent_ids': fields.many2many('project.task', 'project_task_parent_rel', 'task_id', 'parent_id', 'Parent Tasks'),
        #~ 'child_ids': fields.many2many('project.task', 'project_task_parent_rel', 'parent_id', 'task_id', 'Delegated Tasks'),
        #~ 'notes': fields.text('Notes'),
        #~ 'planned_hours': fields.float('Initially Planned Hours', help='Estimated time to do the task, usually set by the project manager when the task is in draft state.'),
        #~ 'effective_hours': fields.function(_hours_get, string='Hours Spent', multi='hours', help="Computed using the sum of the task work done.",
            #~ store = {
                #~ 'project.task': (lambda self, cr, uid, ids, c={}: ids, ['work_ids', 'remaining_hours', 'planned_hours'], 10),
                #~ 'project.task.work': (_get_task, ['hours'], 10),
            #~ }),
        #~ 'remaining_hours': fields.float('Remaining Hours', digits=(16,2), help="Total remaining time, can be re-estimated periodically by the assignee of the task."),
        #~ 'total_hours': fields.function(_hours_get, string='Total', multi='hours', help="Computed as: Time Spent + Remaining Time.",
            #~ store = {
                #~ 'project.task': (lambda self, cr, uid, ids, c={}: ids, ['work_ids', 'remaining_hours', 'planned_hours'], 10),
                #~ 'project.task.work': (_get_task, ['hours'], 10),
            #~ }),
        #~ 'progress': fields.function(_hours_get, string='Progress (%)', multi='hours', group_operator="avg", help="If the task has a progress of 99.99% you should close the task if it's finished or reevaluate the time",
            #~ store = {
                #~ 'project.task': (lambda self, cr, uid, ids, c={}: ids, ['work_ids', 'remaining_hours', 'planned_hours','state'], 10),
                #~ 'project.task.work': (_get_task, ['hours'], 10),
            #~ }),
        #~ 'delay_hours': fields.function(_hours_get, string='Delay Hours', multi='hours', help="Computed as difference between planned hours by the project manager and the total hours of the task.",
            #~ store = {
                #~ 'project.task': (lambda self, cr, uid, ids, c={}: ids, ['work_ids', 'remaining_hours', 'planned_hours'], 10),
                #~ 'project.task.work': (_get_task, ['hours'], 10),
            #~ }),
        #~ 'user_id': fields.many2one('res.users', 'Assigned to'),
        #~ 'delegated_user_id': fields.related('child_ids', 'user_id', type='many2one', relation='res.users', string='Delegated To'),
        #~ 'partner_id': fields.many2one('res.partner', 'Customer'),
        #~ 'work_ids': fields.one2many('project.task.work', 'task_id', 'Work done'),
        #~ 'manager_id': fields.related('project_id', 'analytic_account_id', 'user_id', type='many2one', relation='res.users', string='Project Manager'),
        #~ 'company_id': fields.many2one('res.company', 'Company'),
        #~ 'id': fields.integer('ID', readonly=True),
        #~ 'color': fields.integer('Color Index'),
        #~ 'user_email': fields.related('user_id', 'email', type='char', string='User Email', readonly=True),
    #~ }
    #~ _defaults = {
        #~ 'stage_id': _get_default_stage_id,
        #~ 'project_id': _get_default_project_id,
        #~ 'kanban_state': 'normal',
        #~ 'priority': '2',
        #~ 'progress': 0,
        #~ 'sequence': 10,
        #~ 'active': True,
        #~ 'user_id': lambda obj, cr, uid, context: uid,
        #~ 'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'project.task', context=c),
    #~ }
    #~ _order = "priority, sequence, date_start, name, id"
