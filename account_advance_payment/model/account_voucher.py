# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Jorge Angel Naranjo (jorge_nr@vauxoo.com)
#
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

from openerp.osv import osv, fields
from openerp.tools.translate import _


class account_voucher(osv.Model):
    _inherit = 'account.voucher'
    _columns = {
        'advance_account_id': fields.many2one('account.account', 'Advance Account', required=False, readonly=True, states={'draft': [('readonly', False)]}),
    }
    
    def writeoff_move_line_get(self, cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context=None):
        move_line = super(account_voucher, self).writeoff_move_line_get(cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context=context)
        voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context)
        if move_line and not voucher.payment_option == 'with_writeoff' and voucher.partner_id:
            if voucher.type in ('sale', 'receipt'):
                account_id = voucher.advance_account_id and voucher.advance_account_id.id or voucher.partner_id.property_account_customer_advance.id
            else:
                account_id = voucher.advance_account_id and voucher.advance_account_id.id or voucher.partner_id.property_account_supplier_advance.id
            if not account_id:
                raise osv.except_osv(_('Missing Configuration on Partner !'),
                    _('Please Fill Advance Accounts on Partner !'))
            move_line['account_id'] = account_id
        return move_line

    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=None):
        res = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=context)
        context = context or {}
        if not partner_id:
            return res
        partner_pool = self.pool.get('res.partner')
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        advance_account_id = False
        if ttype in ('sale', 'receipt'):
            advance_account_id = partner.property_account_customer_advance and partner.property_account_customer_advance.id \
                or partner.property_account_receivable and partner.property_account_receivable.id or False
        else:
            advance_account_id = partner.property_account_supplier_advance and partner.property_account_supplier_advance.id \
                or partner.property_account_payable and partner.property_account_payable.id or False
                
        res['value']['advance_account_id'] = advance_account_id

        return res
