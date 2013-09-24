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
from ast import literal_eval

_TASK_STATE = [('new', 'New'), (
    'publish', 'Publish'), ('unpublish', 'Cancel Publish')]


class mail_message(osv.osv):

    _inherit = 'mail.message'

    def button_publish(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        dict_mail = {}
        obj_user = self.pool.get('res.users')

        for obj in self.browse(cr, uid, ids, context=None):
            if obj.model == "mail.group":
                if obj.mail_group_id.id:
                    params = self.pool.get('ir.actions.client').read(cr,
                                                                     uid,
                                                                     [obj.mail_group_id.id],
                                                                     ['params'],
                                                                     context=context)
                    for i in params[0]['params']['domain']:
                        if i[0] == 'model':
                            dict_mail.update({'model': i[2]})
                        elif i[0] == 'res_id':
                            dict_mail.update({'res_id': i[2]})
                        elif i[0] == 'author_id':
                            user_ids = obj_user.search(cr, uid,
                                                       [('name', '=', i[2])], context=context)
                            dict_mail.update({'author_id': obj_user.browse(cr,
                                                                           uid,
                                                                           user_ids,
                                                                           context=context
                                                                           )[0].partner_id.id})
                else:
                    raise osv.except_osv(_('Error'), _("""You may set
                    group where you want publish this comment"""))
            else:
                raise osv.except_osv(_('Error'), _(
                                     """You can not post a comment associated with the model
                %s""" % (obj.model)))
            dict_mail.update({'state': 'publish'})
        dict_mail and self.write(cr, uid, ids, dict_mail, context=context)
        return True

    def button_unpublish(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        dist_history = {}

        for obj in self.browse(cr, uid, ids, context=context):
            if obj.dict_history:
                dist_history = literal_eval(obj.dict_history)
                dist_history.update({'state': 'unpublish'})
        dist_history and self.write(
            cr, uid, ids, dist_history, context=context)
        return True

    _columns = {
        'mail_group_id': fields.many2one('ir.actions.client', 'Grupo',
            domain=[('res_model', '=', 'mail.group'), ('tag', 'ilike', 'mail.wall')]),
        'dict_history': fields.char('History', help="When status change to publish, this field is"
            "setted to storage previos values."),
        'state': fields.selection(_TASK_STATE, 'Related Status', required=True,
        help="The status of your document is automatically changed regarding the selected stage. "
        "For example, if a stage is related to the status 'unPublish', when your document reaches"
        "this stage, it is automatically unPublish."),
    }
    _defaults = {
        'state': 'new',
    }

    def create(self, cr, uid, values, context=None):
        if context is None:
            context = {}
        newid = super(mail_message, self).create(
            cr, uid, values, context=context)
        for obj in self.browse(cr, uid, [newid], context=None):
            dict_history = {'model': obj.model,
                            'res_id': obj.res_id,
                            'author_id': obj.author_id.id}

            dict_history and self.write(cr, uid, [newid],
                                        {'dict_history': dict_history}, context=context)
        return newid
