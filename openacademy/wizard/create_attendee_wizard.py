# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
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

class attendee_memory(osv.osv_memory):
    """
    OpenERP osv memory wizard : create_attendee_wizard
    """
    
    _name = 'openacademy.attendee.memory'
    _description = "Wizard to add attendees"
    
    _columns = {
        'name':fields.char('Name', 64, required=False, readonly=False),
        'partner_id': fields.many2one('res.partner','Partner',required=True),
        'wiz_id':fields.many2one('openacademy.create.attendee.wizard',),
    }
    _defaults = {
        'name': lambda *a: "",
    }
attendee_memory()

class create_attendee_wizard(osv.osv_memory):
    _name = 'openacademy.create.attendee.wizard'
    _columns = {
        'session_id': fields.many2one('openacademy.session', 'Session', required=True,),
        'attendee_ids': fields.one2many('openacademy.attendee.memory', 'wiz_id','Attendees'),
        }
        
    def _get_active_session(self, cr, uid, context=None):
        if not context:
            return False
        else:
            return context.get('active_id')

    _defaults = {
        'session_id': _get_active_session,
    }

    def action_add_attendee(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        if len(context.get('active_ids'))>1:
            session_ids=context.get('active_ids')
        else:
            session_ids=[wizard.session_id.id]
        attendee_pool = self.pool.get('openacademy.attendee')
        for session_id in session_ids:
            for attendee in wizard.attendee_ids:
                attendee_pool.create(cr,uid,{'partner_id':attendee.partner_id.id,
                'session_id':session_id} )
        return {}

create_attendee_wizard()
