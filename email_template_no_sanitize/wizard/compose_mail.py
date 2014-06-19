# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp import SUPERUSER_ID
import base64
from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _


class mail_compose_message(osv.TransientModel):

    _inherit = 'mail.compose.message'

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}

        template_obj = self.pool.get('email.template')
        res = super(mail_compose_message, self).default_get(cr, uid, fields, context=context)
        template_brw = template_obj.browse(cr, uid, res.get('template_id'),
                                           context=context)
        if template_brw.special:
            values = self.generate_email_for_composer(cr, uid,
                                                      res.get('template_id'),
                                                      res.get('res_id'),
                                                      context=context)

            res.update({'body_text':values.get('body', '')})
        return res

    _columns = {
            'body_text':fields.text('Body', help='Used to avoid the sanitize '
                                                 'method and allow send '
                                                 'custom template messages'),

            }

    def send_mail(self, cr, uid, ids, context=None):
        """ Process the wizard content and proceed with sending the related
            email(s), rendering any template patterns on the fly if needed. """
        if context is None:
            context = {}
        ir_attachment_obj = self.pool.get('ir.attachment')
        mail_mail = self.pool.get('mail.mail')
        active_ids = context.get('active_ids')
        template_obj = self.pool.get('email.template')
        is_log = context.get('mail_compose_log', False)

        for wizard in self.browse(cr, uid, ids, context=context):
            temp_id = wizard.template_id
            template_brw = temp_id and template_obj.browse(cr, uid, temp_id,
                                                           context=context)

            if template_brw and template_brw.special and wizard.body_text:
                attach_name = '%s.html' % template_brw.special_name
                mass_mail_mode = wizard.composition_mode == 'mass_mail'
                active_model_pool_name = wizard.model if wizard.model else 'mail.thread'
                active_model_pool = self.pool.get(active_model_pool_name)

                # wizard works in batch mode: [res_id] or active_ids
                res_ids = active_ids if mass_mail_mode and wizard.model and active_ids else [wizard.res_id]
                for res_id in res_ids:
                    # mail.message values, according to the wizard options
                    post_values = {
                        'subject': wizard.subject,
                        'body': '',
                        'parent_id': wizard.parent_id and wizard.parent_id.id,
                        'partner_ids': [partner.id for partner in wizard.partner_ids],
                        'attachment_ids': [attach.id for attach in wizard.attachment_ids],
                        'attachments': [],
                    }
                    # mass mailing: render and override default values
                    if mass_mail_mode and wizard.model:
                        email_dict = self.render_message(cr, uid, wizard, res_id, context=context)
                        post_values['partner_ids'] += email_dict.pop('partner_ids', [])
                        attachment_ids = []
                        for attach_id in post_values.pop('attachment_ids'):
                            new_attach_id = ir_attachment_obj.copy(cr, uid, attach_id, {'res_model': self._name, 'res_id': wizard.id}, context=context)
                            attachment_ids.append(new_attach_id)

                        post_values['attachments'].append((attach_name, wizard.body_text.encode('utf-8')))
                        post_values['attachment_ids'] = attachment_ids
                        post_values.update(email_dict)
                    # post the message
                    subtype = 'mail.mt_comment'
                    post_values.update({'body': ''})
                    msg_id = active_model_pool.message_post(cr, uid, [res_id], type='notification', subtype=subtype, context=context, **post_values)
                    attach_ids = ir_attachment_obj.search(cr, uid,
                                             [('res_model', '=', wizard.model),
                                              ('res_id', '=', res_id),
                                              ('name', '=', attach_name)],
                                              limit=1,
                                              order='id desc',
                                              context=context)

                    self.pool.get('mail.notification')._notify(cr, uid, msg_id, post_values['partner_ids'], context=context)
                    mail_id = mail_mail.create(cr, uid,
                                               {
                                                'model': wizard.model,
                                                'res_id': res_id,
                                                'subject':wizard.subject,
                                                'body_html': wizard.body_text,
                                                'attachment_ids':[(6, 0,
                                                                  attach_ids)],
                                                'auto_delete': True,
                                               }, context=context)
                    mail_mail.send(cr, uid, [mail_id],
                                   recipient_ids=post_values.get('partner_ids'),
                                   context=context)
                    # mass_mailing: notify specific partners, because subtype was False, and no-one was notified

            else:
                return super(mail_compose_message,self).send_mail(cr, uid,
                                                                  ids, context)


        return {'type': 'ir.actions.act_window_close'}

