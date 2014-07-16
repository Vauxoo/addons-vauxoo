# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv, fields
from openerp.tools.translate import _

class project_issue(osv.osv):
    _inherit = "project.issue"
    
    def send_mail_notification(self, cr, uid, ids, context=None):
        '''
        Send mail automatically to change issue to Send Mail Customer.
        '''
        if context is None:
            context = {}
        ctx = {}
        if ids.get('stage_id', False):
            type = self.pool.get('project.task.type').read(cr, uid, ids['stage_id'][0], ['name'])
            if type.get('name', False) == 'Sent Customer Mail':
                self.send_mail_issue(cr, uid, [ids.get('id', [])], context=context)
        
    def send_mail_issue(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context.update({'active_model': 'project_issue', 'active_ids': ids, 'active_id': ids[0]})
        tmp_id = self.pool.get('email.template').search(cr, uid, [(
                    'model_id.model', '=', self._name),
                    ], limit=1, context=context)
        if tmp_id:
            mail_compose_message_pool = self.pool.get('mail.compose.message')
            data = self.browse(cr, uid, ids[0], context=context)
            message = mail_compose_message_pool.onchange_template_id(
                cr, uid, [], template_id=tmp_id[0], composition_mode=None,
                model = self._name, res_id = data.id, context=context)
            mssg = message.get('value', False)
            followers = [x.id for x in data.message_follower_ids]
            mssg.get('partner_ids', {}).extend(followers)
            mssg.update({'model': 'project.issue'})
            mssg_id = mail_compose_message_pool.create(cr, uid, mssg, context=context)
            state = mail_compose_message_pool.send_mail(cr, uid, [mssg_id], context=context)
        return False
    
    def send_tickect_customer(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        tmp_id = self.pool.get('email.template').search(cr, uid, [(
                    'model_id.model', '=', self._name),
                    ], limit=1, context=context)
        ctx = dict(context)
        ctx.update({
            'default_model': 'project.issue',
            'default_res_id': ids[0],
            'default_use_template': bool(tmp_id),
            'default_template_id': tmp_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
        
    _track = {'stage_id': {'project.mt_task_stage': send_mail_notification, }}
