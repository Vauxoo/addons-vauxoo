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

_TASK_STATE = [('new','New'),('publish', 'Publish'),('unpublish', 'Cancel Publish')]

class admin_message(osv.osv):

    _inherit = 'mail.message'

    def button_publish(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        dict_mail,list_history={},[]
        obj_user = self.pool.get('res.users')

        for obj in self.browse(cr,uid,ids,context=None):
            if obj.model == "mail.group":
                if obj.mail_group_id.id:
                    params = self.pool.get('ir.actions.client').read(cr,
                    uid, [obj.mail_group_id.id], ['params'],context=context)
                    for i in params[0]['params']['domain']:
                        if i[0] =='model':
                            dict_mail.update({'model':i[2]})
                        elif i[0]=='res_id':
                            dict_mail.update({'res_id':i[2]})
                        elif i[0]=='author_id':
                            user_ids = obj_user.search(cr,uid,
                            [('name','=',i[2])],context=context)
                            dict_mail.update({'author_id':obj_user.browse(cr,
                            uid,user_ids,context=context)[0].partner_id.id})
                else:
                    raise osv.except_osv(_('Error'), _("""You may set
                    group where you want publish this comment"""))
            else:
                raise osv.except_osv(_('Error'), _(
                """You can not post a comment associated with the model 
                %s"""%(obj.model)))
            
            list_history=[('model',obj.model),
                          ('res_id',obj.res_id),
                          ('author_id',obj.author_id.id)]
            list_history and dict_mail.update({'list_history':list_history,
                              'state':'publish'})
        dict_mail and self.write(cr,uid,ids,dict_mail,context=context) 
        return True

    def button_unpublish(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        dict_mail={}

        for obj in self.browse(cr,uid,ids,context=context):
            for i in literal_eval(obj.dict_history):
                if i[0] =='model':
                    dict_mail.update({'model':i[1]})
                elif i[0]=='res_id':
                    dict_mail.update({'res_id':i[1]})
                elif i[0]=='author_id':
                    dict_mail.update({'author_id':i[1]})
            dict_mail.update({'state':'unpublish'})
        dict_mail and self.write(cr,uid,ids,dict_mail,context=context)
        return True

    _columns = {
        'mail_group_id': fields.many2one('ir.actions.client', 'Grupo',domain=[('res_model','=','mail.group'),('tag','ilike','mail.wall')]),
        'list_history': fields.char('History',help="When status change to publish, this field is seted to storage previos values."),
        'state': fields.selection(_TASK_STATE, 'Related Status', required=True,
        help="The status of your document is automatically changed regarding the selected stage. " \
        "For example, if a stage is related to the status 'unPublish', when your document reaches this stage, it is automatically unPublish."),
    }
    _defaults = {
        'state': 'new',
    }


