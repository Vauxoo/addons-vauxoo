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

from openerp.osv import fields, osv
from openerp.tools.translate import _

class project_task(osv.osv):

    _inherit = 'project.task'
    
    def send_mail_task(self,cr, uid, ids, context=None):
        '''
        Send mail automatically to change task of column Undefinied to Backlog.
        '''
        context = context or {}

        if ids.get('stage_id'):
            if ids['stage_id'][1]=='Backlog':
                
                
                imd_obj = self.pool.get('ir.model.data')
                id_template= imd_obj.search(cr,uid,[('model','=','email.template'),('name','=','template_send_email_task_new')])
                
                res_id= imd_obj.read(cr,uid,id_template,['res_id'])[0]['res_id']
                
                followers = self.read(cr,uid,ids.get('id'),['message_follower_ids'])['message_follower_ids']
                
                ids = [ids.get('id')]
                body_html = self.pool.get('email.template').read(cr,uid,res_id,['body_html']).get('body_html') 
                context.update({'default_template_id':res_id,
                                'default_body': body_html,
                                'default_use_template': True,
                                'default_composition_mode': 'comment',
                                'active_model': 'project.task',
                                'default_partner_ids':followers,
                                'mail_post_autofollow_partner_ids': followers,
                                'active_id': ids and type(ids) is list and \
                                                  ids[0] or ids,
                                'active_ids': ids and type(ids) is list and \
                                                  ids or [ids],
                                })

                mail_obj = self.pool.get('mail.compose.message')
                fields = mail_obj.fields_get(cr, uid)
                mail_ids = mail_obj.default_get(cr, uid, fields.keys(), context=context)
                mail_ids.update({'model':'project.task','body':body_html,'composition_mode':'mass_mail','partner_ids':[(6,0,followers)]})
                mail_ids = mail_obj.create(cr, uid, mail_ids, context=context)
                mail_obj.send_mail(cr, uid, [mail_ids], context=context)

        return False
    
    _track= {'stage_id':{'project.mt_task_stage': send_mail_task,} }


    _columns = {
        'project_leader': fields.char('Project Leader', size=255,readonly=True,help="""Person responsible of task create and task management."""),
    }
    _defaults = {
        'project_leader': lambda self, cr, uid, ctx: uid,
    }

