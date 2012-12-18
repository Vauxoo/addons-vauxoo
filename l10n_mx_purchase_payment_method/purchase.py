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
from osv import osv
from osv import osv, fields

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
    def onchange_partner_id(self, cr, uid, ids, partner_id):
        partner = self.pool.get('res.partner')
        res=super(purchase_order, self).onchange_partner_id(cr, uid, ids, partner_id)
        if partner_id:
            partner_bank_obj=self.pool.get('res.partner.bank')
            bank_partner_id=partner_bank_obj.search(cr, uid, [('partner_id','=',partner_id)])
            pay_method_id=partner.browse(cr,uid,partner_id).pay_method_id.id
            res['value'].update({'acc_payment': bank_partner_id and bank_partner_id[0] or False,'pay_method_id':pay_method_id or False})
        return res
        
    _columns = {
        'acc_payment': fields.many2one ('res.partner.bank', 'Numero de cuenta', readonly=True, states={'draft':[('readonly',False)]},help = 'Es la cuenta con la que el cliente pagará la factura, si no se sabe con cual cuenta se va pagar dejarlo vacío y en el xml aparecerá "No identificado".'),
        'pay_method_id': fields.many2one('pay.method', 'Metodo de Pago', readonly=True, states={'draft':[('readonly',False)]}, help = 'Indica la forma en que se pagó o se pagará la factura, donde las opciones pueden ser: cheque, transferencia bancaria, depósito en cuenta bancaria, tarjeta de crédito, efectivo etc. Si no se sabe como va ser pagada la factura, dejarlo vacío y en el xml aparecerá “No identificado”.'),
    }
    
    def action_invoice_create(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        res=super(purchase_order,self).action_invoice_create( cr, uid, ids, context=context)
        purchase_order_id=self.browse(cr, uid, ids, context=context)[0]
        acc_payment_id=purchase_order_id.acc_payment and purchase_order_id.acc_payment.id or False
        payment_method_id=purchase_order_id.pay_method_id and purchase_order_id.pay_method_id.id or False
        invoice_obj.write(cr, uid, [res], {'acc_payment': acc_payment_id}, context=context)
        invoice_obj.write(cr, uid, [res], {'pay_method_id': payment_method_id}, context=context)
        return res
purchase_order()

