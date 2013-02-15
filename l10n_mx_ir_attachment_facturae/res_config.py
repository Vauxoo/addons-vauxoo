# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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

from openerp.osv import fields, osv
from openerp import pooler
from openerp.tools.translate import _

class l10n_mx_email_config_settings(osv.osv_memory):
    _name = 'l10n.mx.email.config.settings'
    _inherit = 'res.config.settings'
    _order = "id desc"
    

    _columns = {
        'name' : fields.many2one('email.template','Email Template'),
    }

    def get_default_amount(self, cr, uid, fields, context=None):
        cr.execute(""" select max(id) as email_tmp_id from l10n_mx_email_config_settings """)
        dat = cr.dictfetchall()
        if dat:
            email_tmp_id = self.browse(cr, uid, dat[0]['email_tmp_id']).name
            return {'name' : email_tmp_id  and email_tmp_id.id or False}

        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
