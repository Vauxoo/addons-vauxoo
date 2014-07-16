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
        
class mail_compose_message(osv.Model):
    _inherit = 'mail.compose.message'

    def send_mail(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if context.get('active_model', '') == 'project.issue' and context.get('active_id', False):
            proj_type_obj = self.pool.get('project.task.type')
            stage_ids = proj_type_obj.search(cr, uid, [('name', '=', 'Sent Customer Mail')], context=context)
            if stage_ids:
                self.pool.get('project.issue').write(cr, uid, context.get('active_id'),
                    {'stage_id': stage_ids[0],}, context=context)
        return super(mail_compose_message, self).send_mail(cr, uid, ids, context=context)
