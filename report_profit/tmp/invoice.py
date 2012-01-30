# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Javier Duran <javier@vauxoo.com>
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
from osv import fields, osv
from tools import config


class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'



    def _compute_lines(self, cr, uid, ids, name, args, context=None):
        result = {}
        for il in self.browse(cr, uid, ids, context):            
            am_lines = self.move_line_id_cost_get(cr, uid, [il.id])
            total = 0.0
            for m in self.pool.get('account.move.line').browse(cr, uid, am_lines, context):
                total += (m.quantity and (m.debit/m.quantity) or 0.0) - (m.quantity and (m.credit/m.quantity) or 0.0)

            result[il.id] = total
        return result


    def _get_iline_from_amline(self, cr, uid, ids, context={}):
        move = {}
        inv_line_ids = []
        for line in self.pool.get('account.move.line').browse(cr, uid, ids):
            move[line.move_id.id] = True
        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','in',move.keys())], context=context)
            inv_line_ids = self.pool.get('account.invoice.line').search(cr, uid, [('invoice_id','in',invoice_ids)], context=context)
        return inv_line_ids


    def _get_iline_from_invoice(self, cr, uid, ids, context={}):
        move = {}
        inv_line_ids = []
        for invoice in self.pool.get('account.invoice').browse(cr, uid, ids):
            if invoice.state=='open':
                for line in invoice.invoice_line:
                    inv_line_ids.append(line.id)
        return inv_line_ids



    _description = "Last Invoice Price"
    _columns = {
        'last_price': fields.float('Last Price', digits=(16, int(config['price_accuracy']))),
        'acc_cost': fields.function(_compute_lines, method=True, string='Costo', digits=(16, int(config['price_accuracy'])),
            store={
                'account.invoice': (_get_iline_from_invoice, ['state', 'invoice_line'], 50),
                'account.move.line': (_get_iline_from_amline, ['debit','credit','quantity'], 50),
            }, help="The account moves cost of the invoice line"),
    }
    


    def move_line_id_cost_get(self, cr, uid, ids, *args):
        res = []
        for l in self.browse(cr, uid, ids):
            if l.invoice_id.type in ('out_invoice','out_refund'):
                src_account_id =  l.product_id.property_account_expense and l.product_id.property_account_expense.id or False

                if not src_account_id:
    #                raise osv.except_osv('Accion Invalida !', "Producto sin cuenta de costo o inventario asignada!: '%s'" % (l.product_id.name,))
                    continue
                # FIXME - que pasa si la factura no tiene movimiento(draft) o esta cancelada
                if l.invoice_id.move_id:
                    for aml in l.invoice_id.move_id.line_id:
                        if aml.account_id.id==src_account_id and aml.product_id.id==l.product_id.id and aml.quantity==l.quantity:
                            res.append(aml.id)


        return res


    def move_line_id_inv_get(self, cr, uid, ids, *args):
        res = []
        aml_obj = self.pool.get('account.move.line')
        aml_ids = []
        for l in self.browse(cr, uid, ids):
            if l.invoice_id.type in ('out_invoice','out_refund'):
                src_account_id =  l.product_id.property_stock_account_output and l.product_id.property_stock_account_output.id or False
            else:
                src_account_id =  l.product_id.property_stock_account_input and l.product_id.property_stock_account_input.id or False

            if not src_account_id:
#                raise osv.except_osv('Accion Invalida !', "Producto sin cuenta de costo o inventario asignada!: '%s'" % (l.product_id.name,))
                continue
            
            if l.invoice_id.move_id:
                aml_ids = aml_obj.find(cr, uid, mov_id=l.invoice_id.move_id.id, \
                                        acc_id=src_account_id,prd_id=l.product_id.id, \
                                        qty=l.quantity)
                
                if aml_ids:
                    res.append(aml_ids[0])

        return res


account_invoice_line()



class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    

    def button_reset_cost(self, cr, uid, ids, context=None):
        if not context:
            context = {}

        for invoice in self.browse(cr, uid, ids):
            for line in invoice.invoice_line:
                if line.acc_cost:
                    print 'La factura: ',line.invoice_id.name,'  Posee un costo: ',line.acc_cost


         # Update the stored value (fields.function), so we write to trigger recompute
        self.pool.get('account.invoice').write(cr, uid, ids, {'invoice_line':[]}, context=context)    

        return True


account_invoice()

