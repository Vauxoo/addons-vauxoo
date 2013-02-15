# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Israel Fermín Montilla  <israel@openerp.com.ve>
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
###############################################################################
from osv import osv
from osv import fields
from tools.translate import _
import netsvc
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class inherited_stock(osv.osv):
    """
    M321 Customizations for product.picking model
    """
    
    _inherit = 'stock.picking'

    def default_get(self,cr,uid,fields,context=None):
        if context is None:
            context = {}
        
        res = super(inherited_stock,self).default_get(cr,uid,fields,context=context)
        #~ res.update({'total_sale':'noooo'})
        return res
    
    
    def _order_total(self,cr,uid,ids,name,arg,context=None):
        
        if context is None:
            context = {}
        
        if not len(ids):
            return {}
        res = {}
        picking_brw = self.browse(cr,uid,ids,context=context)
        if hasattr(picking_brw[0], "sale_id"):
            for picking in picking_brw: 
                total = picking.sale_id and picking.sale_id.amount_total or 0
                res[picking.id] = total 
        
        return res

    _columns = {
            'pay_state': fields.selection([('paynot','Not Payed'),('2bpay','To pay'),('payed','Payed')],"Pay Control", help="The pay state for this picking"),
            'total_sale':fields.function(_order_total,method=True, type='float',string='Total Sale'),
            'sales_incoterm':fields.related('sale_id','incoterm',relation='stock.incoterms',type='many2one',string='Incoterm',readonly=True),
        }
   
    _defaults = {
            'pay_state':'paynot',
            
            }
            
    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        """ Creates invoice based on the invoice state selected for picking.
        @param journal_id: Id of journal
        @param group: Whether to create a group invoice or not
        @param type: Type invoice to be created
        @return: Ids of created invoices for the pickings
        """
        if context is None:
            context = {}

        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        address_obj = self.pool.get('res.partner.address')
        invoices_group = {}
        inv_type = type
        result = super(inherited_stock, self).action_invoice_create(cr, uid,
                ids, journal_id=journal_id, group=group, type=type,
                context=context)
        picking_ids = result.keys()
        invoice_ids = result.values()
        for picking in self.browse(cr, uid, ids, context=context):
            for pick in picking.move_lines:
                for invoice in invoice_obj.browse(cr, uid, invoice_ids, context=context):
                    for line in invoice.invoice_line:
                        if pick.product_id and line.product_id and \
                           (pick.product_id.id == line.product_id.id) and\
                           pick.product_qty == line.quantity:
                            line.write({'percent_com': pick.percent_com})
        return result

    def change_state(self,cr,uid,ids,context=None):
        if context is None:
            context = {}
        picking_brw = self.browse(cr,uid,ids,context=context) and self.browse(cr,uid,ids,context=context)[0]
        #~ print tuple([(i.product_id.name, i.product_qty) for i in picking_brw.move_lines if i.state != 'done' ])
        if all([False for i in picking_brw.move_lines if i.state == 'confirmed' ]):
            self.write(cr,uid,ids,{'pay_state':'payed'},context=context)
        else:
            e = '\n'.join(['The product %s with quantity %s is not available.' %(i.product_id.name, i.product_qty) for i in picking_brw.move_lines if i.state == 'confirmed' ])
            raise osv.except_osv(_('Want to pay this without picking the availability of these products?'), _(e))
            
            
        return True
        
inherited_stock()



class stock_move(osv.osv):
    
    
    _inherit = 'stock.move'
    _columns = {
        'id_sale':fields.many2one('sale.order','Sale Order'),
        'product_upc':fields.related('product_id','upc',type='char',string='UPC'),
        'product_ean13':fields.related('product_id','ean13',type='char',string='EAN13'),     
        'percent_com':fields.float('Percen Commision', help='Percent commision by price list'), 
    
    }
    
    
stock_move()









