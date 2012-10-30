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
	            'members': fields.many2many('res.users', 'project_user_rel', 'project_id', 'uid', 'Project Members',
            help="Project's members are users who can have an access to the tasks related to this project.", states={'close':[('readonly',True)], 'cancelled':[('readonly',True)]}),
	            }
sprint_kanban()	

class sprint_kanban_tasks(osv.osv):

    _inherit = 'project.task'
    
    _columns={
	 
	    'sprint_id':fields.many2one('sprint.kanban','Sprint',ondelete="cascade"),
	 
		
		
 }
sprint_kanban_tasks()
