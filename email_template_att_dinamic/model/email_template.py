#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: vauxoo consultores (info@vauxoo.com)
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################


from openerp.osv import osv, fields
import ast


class email_template(osv.Model):

    _inherit = "email.template"

    _columns = {
        'att_default': fields.boolean('Add attachment', help='Add attachment of record by default'),
        'att_other_field': fields.text('Add attachment from other filed',
                help='specify from which fields are to get attachments'
                '(only fields with relation to ir.attachment)')
    }


class mail_compose_message(osv.TransientModel):
    _inherit = 'mail.compose.message'

    def onchange_template_id(self, cr, uid, ids, template_id,
                        composition_mode, model, res_id, context=None):
        if not context:
            context = {}

        template_obj = self.pool.get('email.template')

        res = super(mail_compose_message,
                    self).onchange_template_id(cr, uid, ids, template_id,
                            composition_mode, model, res_id, context=context)
        attach = []
        if template_id:

            template = template_obj.browse(cr, uid, template_id, context)

            if template and template.att_default:
                attach = self.pool.get('ir.attachment').search(cr, uid,
                    [('res_id', '=', res_id), ('res_model', '=', model)])

            if template and template.att_other_field:
                att_field_render = template_obj.render_template(cr, uid,
                    template.att_other_field, template.model, res_id, context=context)
                attach += [id_att for id_att in ast.literal_eval("[" + att_field_render + "]") if att_field_render]

        attach += res.get('value', {}).pop('attachment_ids', [])
        res.get('value', {}).update({'attachment_ids': [(6, 0, attach)]})

        return res
