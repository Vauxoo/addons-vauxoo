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

from openerp.osv import osv, fields

class mail_compose_message(osv.TransientModel):
    _inherit = 'mail.compose.message'

    def _get_templates(self, cr, uid, context=None):
        if context is None:
            context = {}
        email_template_obj = self.pool.get('email.template')
        if not email_template_obj.check_access_rights(cr, uid, 'read', raise_exception=False):
            return []
        else:
            return super(mail_compose_message, self)._get_templates(cr, uid, context=context)
        return []


    _columns = {
        # incredible hack of the day: size=-1 means we want an int db column instead of an str one
        'template_id': fields.selection(_get_templates, 'Template', size=-1),
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
