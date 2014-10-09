#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Maria Gabriela Quilarque <gabriela@vauxoo.com>
#    Audited by: Maria Gabriela Quilarque <gabriela@vauxoo.com>
###############################################################################
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
###############################################################################

from openerp.tools.translate import _
from openerp.osv import fields, osv

class user_story_phase(osv.Model):
    _name = "user.story.phase"
    _description = "User Story Phase"

    def _check_recursion(self, cr, uid, ids, context=None):
         if context is None:
            context = {}

         data_phase = self.browse(cr, uid, ids[0], context=context)
         prev_ids = data_phase.previous_phase_ids
         next_ids = data_phase.next_phase_ids
         # it should neither be in prev_ids nor in next_ids
         if (data_phase in prev_ids) or (data_phase in next_ids):
             return False
         ids = [id for id in prev_ids if id in next_ids]
         # both prev_ids and next_ids must be unique
         if ids:
             return False
         # unrelated user_story
         prev_ids = [rec.id for rec in prev_ids]
         next_ids = [rec.id for rec in next_ids]
         # iter prev_ids
         while prev_ids:
             cr.execute('SELECT distinct prv_phase_id FROM user_story_phase_rel WHERE next_phase_id IN %s', (tuple(prev_ids),))
             prv_phase_ids = filter(None, map(lambda x: x[0], cr.fetchall()))
             if data_phase.id in prv_phase_ids:
                 return False
             ids = [id for id in prv_phase_ids if id in next_ids]
             if ids:
                 return False
             prev_ids = prv_phase_ids
         # iter next_ids
         while next_ids:
             cr.execute('SELECT distinct next_phase_id FROM user_story_phase_rel WHERE prv_phase_id IN %s', (tuple(next_ids),))
             next_phase_ids = filter(None, map(lambda x: x[0], cr.fetchall()))
             if data_phase.id in next_phase_ids:
                 return False
             ids = [id for id in next_phase_ids if id in prev_ids]
             if ids:
                 return False
             next_ids = next_phase_ids
         return True

    def _check_dates(self, cr, uid, ids, context=None):
         for phase in self.read(cr, uid, ids, ['date_start', 'date_end'], context=context):
             if phase['date_start'] and phase['date_end'] and phase['date_start'] > phase['date_end']:
                 return False
         return True
#
#    def _compute_progress(self, cr, uid, ids, field_name, arg, context=None):
#        res = {}
#        if not ids:
#            return res
#        for phase in self.browse(cr, uid, ids, context=context):
#            if phase.state=='done':
#                res[phase.id] = 100.0
#                continue
#            elif phase.state=="cancelled":
#                res[phase.id] = 0.0
#                continue
#            elif not phase.task_ids:
#                res[phase.id] = 0.0
#                continue
#
#            tot = done = 0.0
#            for task in phase.task_ids:
#                tot += task.total_hours
#                done += min(task.effective_hours, task.total_hours)
#
#            if not tot:
#                res[phase.id] = 0.0
#            else:
#                res[phase.id] = round(100.0 * done / tot, 2)
#        return res

    _columns = {
        'name': fields.char("Name", size=64, required=True),
        'user_story_id': fields.many2one('user.story', 'User Story', required=True, select=True),
        'state': fields.selection([('draft', 'New'), ('cancelled', 'Cancelled'),('open', 'In Progress'), ('pending', 'Pending'), ('done', 'Done')], 'Status', readonly=True, required=True,
                                  help='If the phase is created the status \'Draft\'.\n If the phase is started, the status becomes \'In Progress\'.\n If review is needed the phase is in \'Pending\' status.\
                                  \n If the phase is over, the status is set to \'Done\'.'),
        'date_start': fields.datetime('Start Date', select=True, help="It's computed by the scheduler according the project date or the end date of the previous phase.", states={'done':[('readonly',True)], 'cancelled':[('readonly',True)]}),
        'date_end': fields.datetime('End Date', help=" It's computed by the scheduler according to the start date and the duration.", states={'done':[('readonly',True)], 'cancelled':[('readonly',True)]}),
        'sequence': fields.integer('Sequence', select=True, help="Gives the sequence order when displaying a list of phases."),
        'duration': fields.float('Duration', required=True, help="By default in days", states={'done':[('readonly',True)], 'cancelled':[('readonly',True)]}),

        'next_phase_ids': fields.many2many('user.story.phase', 'user_story_phase_rel', 'prv_phase_id', 'next_phase_id', 'Next Phases', states={'cancelled':[('readonly',True)]}),

        'previous_phase_ids': fields.many2many('user.story.phase', 'user_story_phase_rel',
            'next_phase_id', 'prv_phase_id', 'Previous Phases', states={'cancelled':[('readonly',True)]}),

        'product_uom': fields.many2one('product.uom', 'Duration Unit of Measure', required=True, help="Unit of Measure (Unit of Measure) is the unit of measurement for Duration", states={'done':[('readonly',True)], 'cancelled':[('readonly',True)]}),

        'constraint_date_start': fields.datetime('Minimum Start Date', help='force the phase to start after this date', states={'done':[('readonly',True)], 'cancelled':[('readonly',True)]}),
        
        'constraint_date_end': fields.datetime('Deadline', help='force the phase to finish before this date', states={'done':[('readonly',True)], 'cancelled':[('readonly',True)]}),
        'user_force_ids': fields.many2many('res.users', string='Force Assigned Users'),
        'user_ids': fields.one2many('user.story.user.allocation', 'phase_id', "Assigned Users",states={'done':[('readonly',True)], 'cancelled':[('readonly',True)]},
            help="The resources on the project can be computed automatically by the scheduler."),
        }
        
#        'task_ids': fields.one2many('project.task', 'phase_id', "Project Tasks", states={'done':[('readonly',True)], 'cancelled':[('readonly',True)]}),
#        'progress': fields.function(_compute_progress, string='Progress', help="Computed based on related tasks"),

    _defaults = {
        'state': 'draft',
        'sequence': 10,
    }
    _order = "user_story_id, date_start, sequence"
    _constraints = [
        (_check_recursion,'Loops in phases not allowed',['next_phase_ids', 'previous_phase_ids']),
        (_check_dates, 'Phase start-date must be lower than phase end-date.', ['date_start', 'date_end']),
    ]

    def onchange_user_story(self, cr, uid, ids, user_story, context=None):
        return {}

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        if not default.get('name', False):
            default.update(name=_('%s (copy)') % (self.browse(cr, uid, id, context=context).name))
        return super(user_story_phase, self).copy(cr, uid, id, default, context)

    def set_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def set_open(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'open'})
        return True

    def set_pending(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'pending'})
        return True

    def set_cancel(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'cancelled'})
        return True

    def set_done(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'done'})
        return True
#
#    def generate_phase(self, cr, uid, phases, context=None):
#        context = context or {}
#        result = ""
#
#        task_pool = self.pool.get('project.task')
#        for phase in phases:
#            if phase.state in ('done','cancelled'):
#                continue
#            # FIXME: brittle and not working if context['lang'] != 'en_US'
#            duration_uom = {
#                'day(s)': 'd', 'days': 'd', 'day': 'd', 'd':'d',
#                'month(s)': 'm', 'months': 'm', 'month':'month', 'm':'m',
#                'week(s)': 'w', 'weeks': 'w', 'week': 'w', 'w':'w',
#                'hour(s)': 'H', 'hours': 'H', 'hour': 'H', 'h':'H',
#            }.get(phase.product_uom.name.lower(), "H")
#            duration = str(phase.duration) + duration_uom
#            result += '''
#    def Phase_%s():
#        effort = \"%s\"''' % (phase.id, duration)
#            start = []
#            if phase.constraint_date_start:
#                start.append('datetime.datetime.strptime("'+str(phase.constraint_date_start)+'", "%Y-%m-%d %H:%M:%S")')
#            for previous_phase in phase.previous_phase_ids:
#                start.append("up.Phase_%s.end" % (previous_phase.id,))
#            if start:
#                result += '''
#        start = max(%s)
#''' % (','.join(start))
#
#            if phase.user_force_ids:
#                result += '''
#        resource = %s
#''' % '|'.join(map(lambda x: 'User_'+str(x.id), phase.user_force_ids))
#
#            result += task_pool._generate_task(cr, uid, phase.task_ids, ident=8, context=context)
#            result += "\n"
#
#        return result
#project_phase()
#



class user_story_user_allocation(osv.Model):
    _name = 'user.story.user.allocation'
    _description = 'Phase User Allocation'
    _rec_name = 'user_id'
    _columns = {
        'user_id': fields.many2one('res.users', 'User', required=True),
        'phase_id': fields.many2one('user.story.phase', 'User Story Phase', ondelete='cascade', required=True),
        'project_id': fields.related('phase_id', 'user_story_id', type='many2one',
            relation="user.story", string='Project', store=True),
        'date_start': fields.datetime('Start Date', help="Starting Date"),
        'date_end': fields.datetime('End Date', help="Ending Date"),
    }

class user_story(osv.Model):
    _inherit = 'user.story'

    def _phase_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0)
        phase_ids = self.pool.get('user.story.phase').search(cr, uid, [('user_story_id', 'in', ids)])
        for phase in self.pool.get('user.story.phase').browse(cr, uid, phase_ids, context):
            res[phase.user_story_id.id] += 1
        return res

    _columns = {
        'phase_ids': fields.one2many('user.story.phase', 'user_story_id', "User Story Phases"),
        'phase_count': fields.function(_phase_count, type='integer', string="Open Phases"),
    }

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        # Prevent double project creation when 'use_tasks' is checked!
        context = dict(context, user_story_creation_in_progress=True)
        context['name'] = "User Story / %s" % (vals['name'])
        if vals.get('type', False) not in ('template','contract'):
            vals['type'] = 'contract'
        user_story_id = super(user_story, self).create(cr, uid, vals, context=context)
        return user_story_id

#    def schedule_phases(self, cr, uid, ids, context=None):
#        context = context or {}
#        if type(ids) in (long, int,):
#            ids = [ids]
#        projects = self.browse(cr, uid, ids, context=context)
#        result = self._schedule_header(cr, uid, ids, context=context)
#        for project in projects:
#            result += self._schedule_project(cr, uid, project, context=context)
#            result += self.pool.get('project.phase').generate_phase(cr, uid, project.phase_ids, context=context)
#
#        local_dict = {}
#        exec result in local_dict
#        projects_gantt = Task.BalancedProject(local_dict['Project'])
#
#        for project in projects:
#            project_gantt = getattr(projects_gantt, 'Project_%d' % (project.id,))
#            for phase in project.phase_ids:
#                if phase.state in ('done','cancelled'):
#                    continue
#                # Maybe it's better to update than unlink/create if it already exists ?
#                p = getattr(project_gantt, 'Phase_%d' % (phase.id,))
#
#                self.pool.get('project.user.allocation').unlink(cr, uid,
#                    [x.id for x in phase.user_ids],
#                    context=context
#                )
#
#                for r in p.booked_resource:
#                    self.pool.get('project.user.allocation').create(cr, uid, {
#                        'user_id': int(r.name[5:]),
#                        'phase_id': phase.id,
#                        'date_start': p.start.strftime('%Y-%m-%d %H:%M:%S'),
#                        'date_end': p.end.strftime('%Y-%m-%d %H:%M:%S')
#                    }, context=context)
#                self.pool.get('project.phase').write(cr, uid, [phase.id], {
#                    'date_start': p.start.strftime('%Y-%m-%d %H:%M:%S'),
#                    'date_end': p.end.strftime('%Y-%m-%d %H:%M:%S')
#                }, context=context)
#        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
