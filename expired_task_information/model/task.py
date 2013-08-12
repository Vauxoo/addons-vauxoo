#
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
#

from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
import time
from datetime import *


class task_expired_config(osv.Model):

    """
    """
    _name = 'task.expired.config'

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(task_expired_config, self).default_get(cr, uid, fields,
                                                           context=context)
        model_ids = self.search(cr, uid, [], context=context)
        if model_ids:
            return self.read(cr, uid, model_ids[0], [], context=context)
        return res

    _columns = {

        'without_change': fields.integer('Without Changes Days',
                                         help='Days number that tasks may '
                                         'have without changes.\n'
                                         'When these days finish an '
                                         'email information is sent'),
        'before_expiry': fields.integer('Before Expiry',
                                        help='Number days before to the '
                                        'expiry day to send an alert '
                                        'for email'),
    }

    def create_config(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        model_ids = self.search(cr, uid, [], context=context)
        dict_read = self.read(cr, uid, ids[0], [], context=context)
        if model_ids:
            self.write(cr, uid, model_ids, dict_read, context=context)
            return {'type': 'ir.actions.act_window_close'}

        return {'type': 'ir.actions.act_window_close'}

    def send_expiration_message(self, cr, uid, context=None):
        context = context or {}
        mail_mail = self.pool.get('mail.mail')
        message = self.pool.get('mail.message')
        task_obj = self.pool.get('project.task')
        work_obj = self.pool.get('project.task.work')
        config_ids = self.search(cr, uid, [], context=context)
        if config_ids:
            config_brw = self.browse(cr, uid, config_ids[0], context=context)
            today = date.today()
            before_expiry = today + timedelta(days=config_brw.before_expiry)
            last_change = today - timedelta(days=config_brw.without_change)
            today = today.strftime('%Y-%m-%d')
            before_expiry = before_expiry.strftime('%Y-%m-%d')
            last_change = last_change.strftime('%Y-%m-%d')
            task_ids = task_obj.search(cr, uid,
                                       [('state', 'not in',
                                        ('done', 'cancelled'))],
                                       context=context)
            for task in task_ids and task_obj.browse(cr, uid, task_ids):
                msg = _('<h2>Information about %s</h2>' % task.name)
                if task.date_deadline and task.date_deadline <= today:
                    msg += _('<p>The task is expired</p>')
                if work_obj.search(cr, uid,
                                   [('date', '<=', last_change),
                                    ('task_id', '=', task.id)],
                                   context) or \
                   message.search(cr, uid,
                                  [('date', '<=', last_change),
                                   ('res_id', '=', task.id)],
                                  context):
                    msg += _('<p>The task has more than %s days without \
                                                                changes</p>'
                             % config_brw.without_change)
                if task.date_deadline and task.date_deadline == before_expiry:
                    msg += _('<p>The task will expire in %s days</p>' %
                             config_brw.before_expiry)
                if msg:
                    mail_id = mail_mail.create(cr, uid,
                                               {
                                                   'model': 'project.task',
                                                   'res_id': task.id,
                                                   'subject': _('Information \
                                                              about task %s' %
                                                                task.id),
                                                   'body_html': '%s' % msg,
                                                   'auto_delete': True,
                                               }, context=context)
                    mail_mail.send(cr, uid, [mail_id],
                                   recipient_ids=[i.id for i in
                                                  task.message_follower_ids],
                                   context=context)

        return True
