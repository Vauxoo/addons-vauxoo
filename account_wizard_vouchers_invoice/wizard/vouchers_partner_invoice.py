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
from openerp.osv import fields, osv

class account_vouchers_invoice_wizard(osv.osv_memory):
    _name = 'account.vouchers.invoice.wizard'
    
    def default_get(self, cr, uid, fields_list=None, context=None):
        res = {}
        if context.get('active_model') == 'account.invoice':
            partner_id = self.pool.get('account.invoice').browse(cr, uid,
                context.get('active_id'), context=context).partner_id.id
            res['partner_id'] = partner_id
        return res
        
    _columns = {
        'partner_id' : fields.many2one('res.partner', 'Partner', readonly=True),
        'voucher_ids' : fields.many2many('account.voucher', 
            'voucher_partner_invoice', 'voucher_id', 'id_wizard',
            'Vouchers Partner', help='Vouchers of this partner in state '\
            'confirm and without invoice associated',),
    }
    
    def apply(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids[0])
        move_line = self.pool.get('account.move.line')
        if context.get('active_model') == 'account.invoice':
            invoice = self.pool.get('account.invoice').browse(cr, uid,
                context.get('active_id'), context=context)
            account_partner_id = invoice.partner_id.\
                property_account_receivable and invoice.partner_id.\
                property_account_receivable.id
            acc_invoice = invoice.account_id.id
            if invoice.move_id:
                for move in invoice.move_id.line_id:
                    if move.account_id.id == acc_invoice:
                        move_acc_inv = move.id
                for voucher in data.voucher_ids:
                    for line in voucher.move_ids:
                        if line.account_id.id == account_partner_id:
                            move_line.reconcile_partial(cr, uid, [line.id,
                                move_acc_inv], 'auto', context)
        return True
