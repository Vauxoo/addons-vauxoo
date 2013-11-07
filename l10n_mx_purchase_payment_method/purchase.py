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


class purchase_order(osv.Model):
    _inherit = 'purchase.order'

    def onchange_partner_id(self, cr, uid, ids, partner_id):
        partner = self.pool.get('res.partner')
        res = super(purchase_order, self).onchange_partner_id(
            cr, uid, ids, partner_id)
        if partner_id:
            partner_bank_obj = self.pool.get('res.partner.bank')
            bank_partner_id = partner_bank_obj.search(
                cr, uid, [('partner_id', '=', partner_id)])
            pay_method_id = partner.browse(
                cr, uid, partner_id).pay_method_id.id
            res['value'].update({'acc_payment': bank_partner_id and bank_partner_id[
                                0] or False, 'pay_method_id': pay_method_id or False})
        return res

    _columns = {
        'acc_payment': fields.many2one('res.partner.bank', 'Account Number',
            readonly=True, states={'draft': [('readonly', False)]}, help='Is \
            the account with which the client pays the invoice, if not know \
            which account will used for pay leave empty and the XML will show \
            "Unidentified".'),
        'pay_method_id': fields.many2one('pay.method', 'Payment Method',
            readonly=True, states={'draft': [('readonly', False)]},
            help='Indicates the way it was paid or will be paid the invoice, \
            where the options could be: check, bank transfer, reservoir in \
            account bank, credit card, cash etc. If not know as will be paid \
            the invoice, leave empty and the XML show “Unidentified”.'),
    }

    def action_invoice_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        res = super(purchase_order, self).action_invoice_create(
            cr, uid, ids, context=context)
        purchase_order_id = self.browse(cr, uid, ids, context=context)[0]
        acc_payment_id = purchase_order_id.acc_payment and purchase_order_id.\
            acc_payment.id or False
        payment_method_id = purchase_order_id.pay_method_id and \
            purchase_order_id.pay_method_id.id or False
        invoice_obj.write(cr, uid, [res], {
                          'acc_payment': acc_payment_id}, context=context)
        invoice_obj.write(cr, uid, [res], {
                          'pay_method_id': payment_method_id}, context=context)
        return res
