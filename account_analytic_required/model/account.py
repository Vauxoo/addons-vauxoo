# coding: utf-8
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


class AccountInvoiceLine(osv.Model):
    _inherit = 'account.invoice.line'

    _columns = {
        'analytic_required':
            fields.boolean('Analytic Required', help='If this field is active,'
                           ' it is required to fill field "account analytic"'),
    }

    def onchange_account_id(self, cr, uid, ids, product_id=False,
                            partner_id=False, inv_type=False,
                            fposition_id=False, account_id=False):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        if not account_id:
            return {}
        res = super(
            AccountInvoiceLine, self).onchange_account_id(
                cr, uid, ids, product_id, partner_id, inv_type, fposition_id,
                account_id)
        account_obj = self.pool.get('account.account')
        if account_id:
            account_brw = account_obj.browse(cr, uid, account_id)
            if account_brw.user_type.analytic_policy == 'always':
                res['value'].update({'analytic_required': True})
            elif account_brw.user_type.analytic_policy == 'never':
                res['value'].update({'analytic_required': False})
                res['value'].update({'analytic_account_id': False})
            else:
                res['value'].update({'analytic_required': False})
        return res
