# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Rodo (rodo@vauxoo.com)
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

from openerp.osv import osv


class Invoice(osv.osv):
    _inherit = 'account.invoice'

    def invoice_pay_customer(self, cr, uid, ids, context=None):
        if not ids:
            return []
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        inv = self.browse(cr, uid, ids[0], context=context)
        inv_ids = []
        result = mod_obj.get_object_reference(cr, uid, 'account_voucher',
                                              'action_voucher_list')
        id_pay = result and result[1] or False
        if inv.type == 'out_invoice' or inv.type == 'out_refund':
            view_type = 'view_vendor_receipt_form'
        else:
            view_type = 'view_vendor_payment_form'
        res = mod_obj.get_object_reference(cr, uid, 'account_voucher',
                                           view_type)
        result = act_obj.read(cr, uid, [id_pay], context=context)[0]
        result['views'] = [(res and res[1] or False, 'form')]
        result['context'] = {
            'default_partner_id': self.pool.get(
                'res.partner')._find_accounting_partner(inv.partner_id).id,
            'default_amount': inv.type in (
                'out_refund', 'in_refund') and -inv.residual or inv.residual,
            'default_reference': inv.name,
            'invoice_type': inv.type,
            'invoice_id': inv.id,
            'default_type': inv.type in (
                'out_invoice', 'out_refund') and 'receipt' or 'payment',
            'type': inv.type in (
                'out_invoice', 'out_refund') and 'receipt' or 'payment'
        }
        result['res_id'] = inv_ids and inv_ids[0] or False
        return result
