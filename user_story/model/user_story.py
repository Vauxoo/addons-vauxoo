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

class user_story(osv.osv):
	"""
	OpenERP Model : User Story
	"""
	
	_name = 'user.story'
		
	_columns = {
		'name':fields.char('Title', size=255, required=True, readonly=False),
		'owner':fields.char('Owner', size=255, required=True, readonly=False),
		'planned_hours': fields.float('Planned Hours'),
		'project_id':fields.many2one('project.project', 'Project', required=True),
		'description':fields.text('Description'),
		'accep_crit_ids':fields.one2many('acceptability.criteria', 'accep_crit_id', 'Acceptability Criteria', required=False),
		'info': fields.text('Other Info'),
		'task_ids':fields.many2many('project.task', 'userstory_task_rel', 'userstory_id', 'task_id', 'Task'),
		'date': fields.date('Date'),
        'user_id':fields.many2one('res.users', 'Create User'),
	}
	_defaults = {
		'name': lambda *a: None,
		'date': lambda *a: time.strftime('%Y-%m-%d'),
        'user_id': lambda self,cr,uid,ctx: uid,
    }
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


