# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import os

from openerp import addons
from openerp.osv import osv
from openerp.tools.translate import _


class survey_send_invitation(osv.TransientModel):
    _inherit = 'survey.send.invitation'

    def action_send(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        record = self.read(cr, uid, ids, [],context=context)
        survey_ids =  context.get('active_ids', [])
        record = record and record[0]
        partner_ids = record['partner_ids']
        user_ref= self.pool.get('res.users')
        survey_ref= self.pool.get('survey')

        model_data_obj = self.pool.get('ir.model.data')
        group_ids = []
        group_id = model_data_obj._get_id(cr, uid, 'base', 'group_survey_user')
        group_id and group_ids.append(model_data_obj.browse(cr, uid, group_id, context).res_id)
        group_id = model_data_obj._get_id(cr, uid, 'answer_survey', 'only_answer_menu')
        group_id and group_ids.append(model_data_obj.browse(cr, uid, group_id, context).res_id)
        group_id = model_data_obj._get_id(cr, uid, 'portal', 'group_portal')
        group_id and group_ids.append(model_data_obj.browse(cr, uid, group_id, context).res_id)

        act_id = self.pool.get('ir.actions.act_window')
        act_id = act_id.search(cr, uid, [('res_model', '=' , 'survey.name.wiz'), \
                        ('view_type', '=', 'form')])
        out = "login,password\n"
        skipped = 0
        existing = ""
        created = ""
        error = ""
        new_user = []
        attachments = {}
        current_sur = survey_ref.browse(cr, uid, context.get('active_id'), context=context)
        exist_user = current_sur.invited_user_ids
        if exist_user:
            for use in exist_user:
                new_user.append(use.id)
        for id in survey_ref.browse(cr, uid, survey_ids):
            self.create_report(cr, uid, [id.id], 'report.survey.form', id.title)
            file = open(addons.get_module_resource('survey', 'report') + id.title +".pdf")
            file_data = ""
            while 1:
                line = file.readline()
                file_data += line
                if not line:
                    break
            file.close()
            attachments[id.title +".pdf"] = file_data
            os.remove(addons.get_module_resource('survey', 'report') + id.title +".pdf")

        for partner in self.pool.get('res.partner').browse(cr, uid, partner_ids):
            if not partner.email:
                skipped+= 1
                continue
            user = user_ref.search(cr, uid, [('login', "=", partner.email)])
            if user:
                if user[0] not in new_user:
                    new_user.append(user[0])
                user = user_ref.browse(cr, uid, user[0])
                user_ref.write(cr, uid, user.id, {'survey_id':[[6, 0, survey_ids]]})
                mail = record['mail']%{'login':partner.email, 'passwd':user.password, \
                                            'name' : partner.name}
                if record['send_mail_existing']:
                    vals = {
                        'state': 'outgoing',
                        'subject': record['mail_subject_existing'],
                        'body_html': '<pre>%s</pre>' % mail,
                        'email_to': partner.email,
                        'email_from': record['mail_from'],
                    }
                    self.pool.get('mail.mail').create(cr, uid, vals, context=context)
                    existing+= "- %s (Login: %s,  Password: %s)\n" % (user.name, partner.email, \
                                                                      user.password)
                continue

            passwd= self.genpasswd()
            out+= partner.email + ',' + passwd + '\n'
            mail= record['mail'] % {'login' : partner.email, 'passwd' : passwd, 'name' : partner.name}
            if record['send_mail']:
                vals = {
                        'state': 'outgoing',
                        'subject': record['mail_subject'],
                        'body_html': '<pre>%s</pre>' % mail,
                        'email_to': partner.email,
                        'email_from': record['mail_from'],
                }
                if attachments:
                    vals['attachment_ids'] = [(0,0,{'name': a_name,
                                                    'datas_fname': a_name,
                                                    'datas': str(a_content).encode('base64')})
                                                    for a_name, a_content in attachments.items()]
                ans = self.pool.get('mail.mail').create(cr, uid, vals, context=context)
                if ans:
                    res_data = {'name': partner.name or _('Unknown'),
                                'login': partner.email,
                                'password': passwd,
                                'address_id': partner.id,
                                'groups_id': [[6, 0, group_ids]],
                                'action_id': act_id[0],
                                'survey_id': [[6, 0, survey_ids]]
                               }
                    user = user_ref.create(cr, uid, res_data)
                    if user not in new_user:
                        new_user.append(user)
                    created+= "- %s (Login: %s,  Password: %s)\n" % (partner.name or _('Unknown'),\
                                                                      partner.email, passwd)
                else:
                    error+= "- %s (Login: %s,  Password: %s)\n" % (partner.name or _('Unknown'),\
                                                                    partner.email, passwd)

        new_vals = {}
        new_vals.update({'invited_user_ids':[[6,0,new_user]]})
        survey_ref.write(cr, uid, context.get('active_id'),new_vals)
        note= ""
        if created:
            note += 'Created users:\n%s\n\n' % (created)
        if existing:
            note +='Already existing users:\n%s\n\n' % (existing)
        if skipped:
            note += "%d contacts where ignored (an email address is missing).\n\n" % (skipped)
        if error:
            note += 'Email not send successfully:\n====================\n%s\n' % (error)
        context.update({'note' : note})
        return {
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'survey.send.invitation.log',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
