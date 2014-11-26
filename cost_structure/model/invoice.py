# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

from openerp.osv import osv, fields


class account_invoice(osv.Model):

    _inherit = 'account.invoice'

    _columns = {
        'cancel_check': fields.boolean('Cancel',
            help="Fenield to indicate if invoice was canceled "),
    }

    _defaults = {
        'cancel_check': False
    }

#    def action_number(self, cr, uid, ids, context=None):
#        '''
#        Modified to compute cost for product in the moment proccess order
#        '''
#        res = super(account_invoice,self).action_number(cr, uid, ids, context=context)
#        invoice_brw = self.browse(cr,uid,ids,context=context)[0]
#        cost_comp_obj = self.pool.get('compute.cost')
#        product_obj = self.pool.get('product.product')
#        if invoice_brw.type in ['in_invoice','in_refund','out_refund']:
#            product_ids = [l.product_id and l.product_id.id for l in invoice_brw.invoice_line]
#            cost = cost_comp_obj.compute_cost(cr,uid,ids,context=context,products=product_ids,period=invoice_brw and  \
#                                invoice_brw.period_id and \
#                                invoice_brw.period_id.id,fifo=False,lifo=False,date=invoice_brw.date_invoice)
#        return res


#    def action_cancel(self, cr, uid, ids, *args):
#        '''
#        Modified to compute cost for product in the moment cancel order
#        '''
#        context = {}
#        context.update({'invoice_cancel':True})
#        res = super(account_invoice,self).action_cancel(cr, uid, ids, *args)
#        invoice_brw = self.browse(cr,uid,ids,context=context)[0]
#        cost_comp_obj = self.pool.get('compute.cost')
#        product_obj = self.pool.get('product.product')
#        if invoice_brw.type != 'out_invoice':
#            product_ids = [l.product_id and l.product_id.id for l in invoice_brw.invoice_line]
#            cost = cost_comp_obj.compute_cost(cr,uid,ids,context=context,products=product_ids,period=invoice_brw and  \
#                            invoice_brw.period_id and \
#                            invoice_brw.period_id.id,fifo=False,lifo=False,date=invoice_brw.date_invoice)
#        return res


class account_invoice_line(osv.Model):

    _inherit = 'account.invoice.line'
    _columns = {

        'aux_financial': fields.float('Total Financial aux',
            help="Total financial at the time of the calculation of cost\
                through the validation of this invoice"),
        'aux_qty': fields.float('Total Qty',
            help="Current Number of calculating the time cost\
                to this invoice"),

    }
