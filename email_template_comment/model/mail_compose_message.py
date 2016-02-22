# coding: utf-8
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
##########################################################################


from openerp.osv import osv


class MailComposeMessage(osv.TransientModel):

    _inherit = 'mail.compose.message'

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}

        email_template_obj = self.pool.get('mail.template')
        result = super(MailComposeMessage, self).default_get(
            cr, uid, fields, context=context)

        template_id = context.get('default_template_id', [])

        template_id = isinstance(template_id, (int, long)) and [
            template_id] or template_id
        for template in email_template_obj.browse(cr, uid, template_id, context=context):
            if template.composition_mode_comment:
                result['composition_mode'] = 'comment'

        return result
