# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Juan Carlos Hernandez Funes (info@vauxoo.com)
#    Planned by: Moises Augusto Lopez Calderon (info@vauxoo.com)
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


class document_page(osv.Model):

    _name = 'document.page'

    _inherit = ['document.page','mail.thread', 'ir.needaction_mixin']

    def write(self, cr, uid, ids, vals, context=None):
        document_browse = self.browse(cr, uid, ids and type(ids) is list and \
                                      ids[0] or ids, context=context)
        
        result = super(document_page, self).write(cr, uid, ids, vals, context)
        if context.get('stop'):
            return result
        context.update({'default_body':_(u'The document %s has been modified' %
                                         document_browse.name  ),
                        'default_parent_id': False,
                        'mail_post_autofollow_partner_ids': [],
                        'default_attachment_ids': [],
                        'mail_post_autofollow': True,
                        'default_composition_mode': 'comment',
                        'default_partner_ids': [],
                        'default_model': 'document.page',
                        'active_model': 'document.page',
                        'default_res_id': ids and type(ids) is list and \
                                          ids[0] or ids,
                        'active_id': ids and type(ids) is list and \
                                          ids[0] or ids,
                        'active_ids': ids and type(ids) is list and \
                                          ids or [ids],
                        'stop':True,
                        })

        self.create_history(cr, uid, ids, vals, context)
        mail_obj = self.pool.get('mail.compose.message')
        fields = mail_obj.fields_get(cr, uid)
        mail_dict = mail_obj.default_get(cr, uid,fields.keys() , context)
        mail_ids = mail_obj.create(cr, uid, mail_dict, context=context)
        mail_obj.send_mail(cr, uid, [mail_ids], context=context)
        
        
        return result

