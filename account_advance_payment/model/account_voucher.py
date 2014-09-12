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


class account_voucher(osv.Model):
    _inherit = 'account.voucher'
    _columns = {
        'trans_type': fields.selection([
            ('normal', 'Payments'),
            ('advance', 'Advance'),
        ], 'Transaction Type', select=True, track_visibility='always',
            help="""Payments.- Normal payment is made. \nAdvance.- Advance payment of custom or supplier"""),
    }

    _defaults = {
        'trans_type': 'normal',
    }

    def writeoff_move_line_get(self, cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context=None):
        move_line = super(account_voucher, self).writeoff_move_line_get(cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context=context)
        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        if move_line and not voucher.payment_option == 'with_writeoff' and voucher.partner_id:
            if voucher.type in ('sale', 'receipt'):
                account_id = voucher.partner_id.property_account_supplier_advance.id
            else:
                account_id = voucher.partner_id.property_account_customer_advance.id
            move_line['account_id'] = account_id
        return move_line

    def onchange_account_advance_payment(self, cr, uid, ids, trans_type, context=None):
        return True
