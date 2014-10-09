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
from openerp.osv import osv


class document_page(osv.Model):

    _name = 'document.page'

    def _check_all(self, cr, uid, ids, field, context=None):

        context = context or {}

        return field == 'new' and ids.get('state') in context or \
            field == 'changed' and ids.get('state') in context.get('states')

    def _check_new(self, cr, uid, ids, context=None):

        context = context or {}
        context.update({'draft': True})
        return self._check_all(cr, uid, ids, 'new', context)

    def _check_changed(self, cr, uid, ids, context=None):

        context = context or {}
        context.update({'states': ['review', 'menucreated', 'published']})
        return self._check_all(cr, uid, ids, 'changed', context)

    _inherit = ['document.page', 'mail.thread', 'ir.needaction_mixin']

    _track = {
        'state': {
            'document_page_comments.document_page_changed': _check_changed,
            'document_page_comments.document_page_new': _check_new,
        },
    }

#    def write(self, cr, uid, ids, vals, context=None):
#        document_browse = self.browse(cr, uid, ids and type(ids) is list and \
#                                      ids[0] or ids, context=context)
#
#        result = super(document_page, self).write(cr, uid, ids, vals, context)
#        if context.get('stop'):
#            return result
#        context.update({'default_body':_(u'The document %s has been modified' %
#                                         document_browse.name  ),
#                        'default_parent_id': False,
#                        'mail_post_autofollow_partner_ids': [],
#                        'default_attachment_ids': [],
#                        'mail_post_autofollow': True,
#                        'default_composition_mode': 'comment',
#                        'default_partner_ids': [],
#                        'default_model': 'document.page',
#                        'active_model': 'document.page',
#                        'default_res_id': ids and type(ids) is list and \
#                                          ids[0] or ids,
#                        'active_id': ids and type(ids) is list and \
#                                          ids[0] or ids,
#                        'active_ids': ids and type(ids) is list and \
#                                          ids or [ids],
#                        'stop':True,
#                        })
#
#        self.create_history(cr, uid, ids, vals, context)
#        mail_obj = self.pool.get('mail.compose.message')
#        fields = mail_obj.fields_get(cr, uid)
#        mail_dict = mail_obj.default_get(cr, uid,fields.keys() , context)
#        mail_ids = mail_obj.create(cr, uid, mail_dict, context=context)
#        mail_obj.send_mail(cr, uid, [mail_ids], context=context)
#
#
#        return result
