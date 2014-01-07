
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
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
from openerp import SUPERUSER_ID, tools
from openerp.tools.translate import _


class res_company(osv.Model):
    _inherit = 'res.company'

    def _get_captcha(self, cr, uid, ids, field_names, arg, context=None):
        if context is None:
            context = {}
        res = {}
        obj_captcha = self.pool.get('res.captcha')
        
        captcha_ids = obj_captcha.search(cr, SUPERUSER_ID,
                                         [('company_id', '=', 1)], context=context)
        c_brw = obj_captcha.browse(
            cr, SUPERUSER_ID, captcha_ids, context=context)
        for i in ids:
            res[i] = c_brw and c_brw[
                0].recaptcha_key or 'CONFIGURE YOUR CAPTCHA'
        return res

    _columns = {
        'recaptcha_id': fields.function(_get_captcha,
                                        string='Captcha Public Key',
                                        type='char',
                                        help="Computed captcha"),
    }
