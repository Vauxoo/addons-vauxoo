# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Juan Carlos Funes (juan@vauxoo.com)
#    Coded by: Luis Torres (luis_t@vauxoo.com)
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Coded by: isaac (isaac@vauxoo.com)
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
from openerp.osv import fields, osv


class res_partner_bank(osv.Model):
    _inherit = 'res.partner.bank'

    def _get_take_digits(self, cr, uid, ids, field, args, context=None):
        if context is None:
            context = {}
        result = {}
        res = ''
        n = -1
        for last in self.browse(cr, uid, ids, context=context):
            for digit in last.acc_number[::-1]:
                if(digit.isdigit() == True) and len(res) < 4:
                    res = digit+res
            result[last.id] = res
        return result

    _columns = {
        'clabe': fields.char('Clabe Interbancaria', size=64, required=False),
        'last_acc_number': fields.function(_get_take_digits, method=True,
            type='char', string="Ultimos 4 digitos", size=4, store=True),
        'currency2_id': fields.many2one('res.currency', 'Currency',),
        'reference' :fields.char('Reference', size=64, help='Reference used in this bank'),
    }
