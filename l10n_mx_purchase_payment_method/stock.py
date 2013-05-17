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
from openerp.tools.translate import _
from openerp import pooler, tools


class stock_picking(osv.Model):
    _inherit = 'stock.picking'

    def action_invoice_create(self, cursor, user, ids, journal_id=False,
                              group=False, type='out_invoice', context=None):
        if context is None:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        purchase_obj = self.pool.get('purchase.order')
        picking_id__invoice_id_dict = super(
            stock_picking, self).action_invoice_create(cursor, user, ids,
                journal_id=journal_id, group=group, type=type, context=context)
        for picking_id in picking_id__invoice_id_dict.keys():
            invoice_id = picking_id__invoice_id_dict[picking_id]
            purchase_id = self.browse(
                cursor, user, picking_id, context=context).purchase_id.id
            if purchase_id:
                purchase_order_id = purchase_obj.browse(
                    cursor, user, purchase_id, context=context)
                acc_payment_id = purchase_order_id.acc_payment and \
                    purchase_order_id.acc_payment.id or False
                payment_method_id = purchase_order_id.pay_method_id and \
                    purchase_order_id.pay_method_id.id or False
                invoice_obj.write(cursor, user, [invoice_id], {
                    'acc_payment': acc_payment_id}, context=context)
                invoice_obj.write(cursor, user, [invoice_id], {
                    'pay_method_id': payment_method_id}, context=context)
        return picking_id__invoice_id_dict
