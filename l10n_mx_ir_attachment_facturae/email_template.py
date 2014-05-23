#!/usr/bin/python
# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
#
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
#######################################################################################
from openerp.osv import osv, fields

class mail_compose_message(osv.TransientModel):
    _inherit = 'mail.compose.message'

    def onchange_template_id(self, cr, uid, ids, template_id, composition_mode, model, res_id, context=None):
        if not context:
            context = {}
        attachment_obj = self.pool.get('ir.attachment.facturae.mx')
        res = super(mail_compose_message, self).onchange_template_id(cr, uid, ids, template_id, composition_mode, model, res_id, context=context)
        if context.get('active_model', '') == 'ir.attachment.facturae.mx' and context.get('active_id', False):
            attachments = []
            data = attachment_obj.browse(cr, uid, [context.get('active_id')], context=context)[0]
            data.file_pdf and attachments.append(data.file_pdf.id)
            data.file_xml_sign and attachments.append(data.file_xml_sign.id)
            res.get('value', {}).update({'attachment_ids': [(6, 0, attachments)]})
        return res
