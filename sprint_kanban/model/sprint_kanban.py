# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


class sprint_kanban(osv.Model):

    def set_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True

    def set_cancel(self, cr, uid, ids, context=None):

        self.write(cr, uid, ids, {'state': 'cancelled'}, context=context)
        return True

    def set_pending(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'pending'}, context=context)
        return True

    def set_open(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'open'}, context=context)
        return True

    _name = 'sprint.kanban'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
        'use_phases': fields.boolean('Phases',
                                     help="""Check this field if you plan
                                             to use phase-based scheduling"""),
        'name': fields.char('Name Sprint', 264, required=True),
        'project_id': fields.many2one('project.project', 'Project',
                                      ondelete="cascade"),
        'description': fields.text('Description'),
        'datestart': fields.date('Start Date'),
        'dateend': fields.date('End Date'),
        'color': fields.integer('Color Index'),
        'members': fields.many2many('res.users', 'project_user_rel',
                                    'project_id', 'uid', 'Project Members',
                                    states={'close': [('readonly', True)],
                                            'cancelled': [('readonly', True)],
                                            }),
        'priority': fields.selection([('4', 'Very Low'),
                                      ('3', 'Low'),
                                      ('2', 'Medium'),
                                      ('1', 'Important'),
                                      ('0', 'Very important')],
                                     'Priority', select=True),
        'state': fields.selection([('draft', 'New'),
                                   ('open', 'In Progress'),
                                   ('cancelled', 'Cancelled'),
                                   ('pending', 'Pending'),
                                   ('done', 'Done')],
                                  'Status', required=True,),
        'user_id': fields.many2one('res.users', 'Assigned to'),
        'kanban_state': fields.selection([('normal', 'Normal'),
                                          ('blocked', 'Blocked'),
                                          ('done', 'Ready To Pull')],
                                         'Kanban State',
                                         help="""A task's kanban state indicate
                                                 special situations
                                                 affecting it:\n
                                               * Normal is the default
                                                 situation\n"
                                               * Blocked indicates something
                                                 is preventing the progress
                                                 of this task\n
                                               * Ready To Pull indicates the
                                                 task is ready to be pulled
                                                 to the next stage""",
                                         readonly=True, required=False),
    }

    def set_kanban_state_blocked(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'kanban_state': 'blocked'}, context=context)
        return False

    def set_kanban_state_normal(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'kanban_state': 'normal'}, context=context)
        return False

    def set_kanban_state_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'kanban_state': 'done'}, context=context)
        return False

    def set_priority(self, cr, uid, ids, priority, *args):
        return self.write(cr, uid, ids, {'priority': priority})

    def set_high_priority(self, cr, uid, ids, *args):
        return self.set_priority(cr, uid, ids, '1')

    def set_normal_priority(self, cr, uid, ids, *args):
        return self.set_priority(cr, uid, ids, '2')

    _defaults = {
        'state': 'draft',
        'priority': '1',
    }


class sprint_kanban_tasks(osv.Model):

    _inherit = 'project.task'

    _columns = {
        'use_phases': fields.boolean('Phases',
                                     help="""Check this field if you plan
                                             to use phase-based scheduling"""),
        'sprint_id': fields.many2one('sprint.kanban', 'Sprint',
                                     ondelete="cascade"),
        'url_branch': fields.char('Url Branch', 264),
        'merge_proposal': fields.char('Merge Proposal', 264),
        'blueprint': fields.char('Blueprint', 264),
        'res_id': fields.char('Revno', 64),
    }
