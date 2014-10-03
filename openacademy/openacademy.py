# -*- encoding: utf-8 -*-
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time


class Course(osv.osv):

    """
    OpenERP Model : openacademy
    """
    _name = 'openacademy.course'
    _description = 'Courses'

    _columns = {
        'name': fields.char('Name', 64, required=True, translate=True),
        'description': fields.text('Description'),
        'responsible_id': fields.many2one('res.users', 'Responsible', required=False, ondelete='set null', select=True),
        'session_ids': fields.one2many('openacademy.session', 'course_id', 'Sessions', required=False),

    }

    def _check_description(self, cr, user, ids):
        for s in self.browse(cr, user, ids):
            if s.description == s.name:
                return False
        return True

    _constraints = [
        (_check_description, _('Error: Please try another different description and Name different between them'), ['name', 'description']),
    ]

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _('The Name of the Courses must be unique !')),
    ]

    # Allow to make a duplicate Course
    def copy(self, cr, uid, id, defaults, context=None):
        previous_name = self.browse(cr, uid, id, context=context).name
        new_name = 'Copy of %s' % previous_name
        list = self.search(cr, uid, [('name', 'like', new_name)], context=context)
        if len(list) > 0:
            new_name = '%s (%s)' % (new_name, len(list) + 1)
        defaults['name'] = new_name
        return super(Course, self).copy(cr, uid, id, defaults, context=context)
Course()


class Session(osv.osv):

    """
    OpenERP Model : Session
    """

    _name = 'openacademy.session'
    _description = 'Sessions For Courses'

    def _get_remaining_seats_percent(self, seats, attendee_list):
        return seats and ((100.0 * (seats - len(attendee_list))) / seats) or 0

    def _get_attendee_count(self, cr, uid, ids, name, args, context=None):
        res = {}
        for session in self.browse(cr, uid, ids, context=context):
            res[session.id] = len(session.attendee_ids)
        return res

    def _remaining_seats_percent(self, cr, uid, ids, field_name, arg, context):
        result = {}
        sessions = self.browse(cr, uid, ids, context)
        for s in sessions:
            result[s.id] = self._get_remaining_seats_percent(s.seats, s.attendee_ids)
        return result

    def onchange_remaining_seats(self, cr, user, ids, seats, attendee_ids):
        res = {}
        if seats >= 0:
            res['value'] = {'remaining_seats_percent': self._get_remaining_seats_percent(seats, attendee_ids),
                            }
        else:
            res['warning'] = {
                'title': 'Warning',
                'message': _('You cannot have negative seats'),
            }
        return res

    _columns = {
        'name': fields.char('Name', 64, required=True, readonly=False),
        'start_date': fields.date('Start Date'),
        'duration': fields.float('Duration', digits=(6, 2), help="Duration in days"),
        'seats': fields.integer('Seats'),
        'course_id': fields.many2one('openacademy.course', 'Course', required=True),
        'instructor_id': fields.many2one('res.partner', 'Instructor', required=False,
        domain=['|', ('is_instructor', '=', True),
        ('category_id.name', 'in', ('Teacher Level 1', 'Teacher Level 2'))]
        ),
        'attendee_ids': fields.one2many('openacademy.attendee',
                                        'session_id', 'Attendees', ),
        'remaining_seats_percent': fields.function(_remaining_seats_percent,
                                method=True, type='float',
                                string='Remaining seats'),
        'active': fields.boolean('Active', required=False),
        'attendee_count': fields.function(_get_attendee_count,
                    type='integer', string='Attendee Count',
                    method=True),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
        ], 'State', select=True, readonly=True),
    }

    def action_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def action_confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)

    def action_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)

    _defaults = {
        'start_date': lambda *a: time.strftime('%Y-%m-%d'),
        'active': True,
        'state': 'draft',
    }

    def compara(self, cr, uid, context=None):
        # Business Object Compare
        return True

Session()


class Attendee(osv.osv):
    _name = 'openacademy.attendee'
    _rec_name = 'partner_id'
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True,
            ondelete="cascade"),
        'session_id': fields.many2one('openacademy.session', 'Session',
            required=True,
            ondelete="cascade"),
    }
Attendee()
