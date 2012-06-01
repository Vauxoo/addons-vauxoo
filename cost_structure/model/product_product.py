#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
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
################################################################################

from osv import fields, osv
import tools
from tools.translate import _
from tools import config
import netsvc
import decimal_precision as dp
from tools.sql import drop_view_if_exists

class product_product(osv.osv):
    
    _inherit = 'product.product'
    
    def _structur_cost_status(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        if not ids:
            return res
        for product in self.browse(cr,uid,ids,context=context):
            res[product.id] = False
            if product.property_cost_structure:
                res[product.id] = True
        
        return res
        
    
    _columns = {
    'property_cost_structure': fields.property(
    'cost.structure',
    type='many2one',
    relation='cost.structure',
    string="Cost and Price Structure",
    method=True,
    view_load=True,
    help="For the current product, this cost and price strucuture will define how the behavior of the price and cost computation "),
    'cost_ult': fields.related('property_cost_structure', 'cost_ult', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Last Cost',help="Last Cost"),
    'qty_ult': fields.related('property_cost_structure', 'qty_ult', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Last Qty'),
    'cost_prom': fields.related('property_cost_structure', 'cost_prom', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'cost_suppler': fields.related('property_cost_structure', 'cost_suppler', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Supplier Cost'),
    'cost_ant': fields.related('property_cost_structure', 'cost_ant', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Ant Cost'),
    'qty_ant': fields.related('property_cost_structure', 'qty_ant', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Ant Qty'),
    'ult_om': fields.related('property_cost_structure', 'ult_om', relation='product.uom', type='many2one', string='Ult UOM'),
    'prom_om': fields.related('property_cost_structure', 'prom_om',relation='product.uom', type='many2one', string='UOM Prom'),
    'ant_om': fields.related('property_cost_structure', 'ant_om', relation='product.uom', type='many2one', string='UOM Ant'),
    'cost_to_price': fields.related('property_cost_structure', 'cost_to_price', type='selection', string='Average Cost'),
    'date_cost_ult': fields.related('property_cost_structure', 'date_cost_ult', type='datetime', string='Date'),
    'date_ult_om': fields.related('property_cost_structure', 'date_ult_om', type='datetime', string='Date'),
    'date_cost_prom': fields.related('property_cost_structure', 'date_cost_prom', type='datetime', string='Date'),
    'date_prom_om': fields.related('property_cost_structure', 'date_prom_om', type='datetime', string='Date'),
    'date_cost_suppler': fields.related('property_cost_structure', 'date_cost_suppler', type='datetime', string='Date'),
    'date_ant_om': fields.related('property_cost_structure', 'date_ant_om', type='datetime', string='Date'),
    'date_cost_ant': fields.related('property_cost_structure', 'date_cost_ant', type='datetime', string='Date'),
    'date_cost_to_price': fields.related('property_cost_structure', 'date_cost_to_price', type='datetime', string='Date'),
    'method_cost_ids': fields.related('property_cost_structure', 'method_cost_ids',relation='method.price', type='one2many', string='Method Cost',),
    'status_bool':fields.function(_structur_cost_status, method=True,type="boolean",store=True, string='Status Price'),
    }
    
    
    def write(self,cr,uid,ids,vals,context=None):

        product_brw = self.browse(cr,uid,ids and ids[0],context=context)
        if product_brw.property_cost_structure and 'property_cost_structure' in vals:
            raise osv.except_osv(_('Error'), _('The product already has a cost structure'))
        
        method_obj = self.pool.get('method.price')
        method_id = []
        if vals.get('property_cost_structure',False):
            if vals.get('method_cost_ids',False):
                for i in vals.get('method_cost_ids'):
                    if i[2] and i[2].get('cost_structure_id',False):
                        pass
                    else:
                        i[2] and i[2].update({'cost_structure_id':vals.get('property_cost_structure',False) or []})
                        print "i[2]",i[2]
                        method_id = i[2] and method_obj.create(cr,uid,i[2],context=context)
                
                method_id and 'method_cost_ids' in vals  and vals.pop('method_cost_ids')
            else:
                'method_cost_ids' in vals and not vals['method_cost_ids'] and vals.pop('method_cost_ids')
        
        else:
            if vals.get('method_cost_ids',False):
                for i in vals.get('method_cost_ids'):
                    if i[2] and i[2].get('cost_structure_id',False):
                        pass
                    else:
                        i[2] and i[2].update({'cost_structure_id':product_brw and product_brw.property_cost_structure and product_brw.property_cost_structure.id or []})
                        method_id = i[2] and method_obj.create(cr,uid,i[2],context=context)
                
                method_id and 'method_cost_ids' in vals  and vals.pop('method_cost_ids')
                        
            
            else:
                'method_cost_ids' in vals and not vals['method_cost_ids'] and vals.pop('method_cost_ids')
        return super(product_product,self).write(cr,uid,ids,vals,context=context)
        

    def price_get(self, cr, uid, ids, ptype='list_price', context=None):
        if context is None:
            context = {}

        if 'currency_id' in context:
            pricetype_obj = self.pool.get('product.price.type')
            price_type_id = pricetype_obj.search(cr, uid, [('field','=',ptype)])[0]
            price_type_currency_id = pricetype_obj.browse(cr,uid,price_type_id).currency_id.id
        res = {}
        product_uom_obj = self.pool.get('product.uom')
        for product in self.browse(cr, uid, ids, context=context):
            ptype = ptype ==  'list_price'  and 'list_price' or 'cost_ult'
            res[product.id] = product[ptype] or 0.0
            if ptype == 'list_price':
                res[product.id] = (res[product.id] * (product.price_margin or 1.0)) + \
                        product.price_extra
            if 'uom' in context:
                uom = product.uos_id or product.uom_id
                res[product.id] = product_uom_obj._compute_price(cr, uid,
                        uom.id, res[product.id], context['uom'])
            # Convert from price_type currency to asked one
            if 'currency_id' in context:
                # Take the price_type currency from the product field
                # This is right cause a field cannot be in more than one currency
                res[product.id] = self.pool.get('res.currency').compute(cr, uid, price_type_currency_id,
                    context['currency_id'], res[product.id],context=context)

        return res





product_product()


class report_cost(osv.osv):
    _name = "report.cost"
    _auto = False
    _order= "date desc"    
    _columns = {
        'date': fields.date('Date Invoice', readonly=True),
        'product_id':fields.many2one('product.product', 'Product', readonly=True, select=True),
        'quantity': fields.float('# of Products', readonly=True),
        'price_unit': fields.float('Unit Price', readonly=True),
        'last_cost': fields.float('Last Cost', readonly=True),
        'price_subtotal': fields.float('Subtotal Price', readonly=True),
        'uom_id': fields.many2one('product.uom', ' UoM', readonly=True),
        'type_inv': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
            ],'Type', readonly=True, select=True),
        'invoice_id':fields.many2one('account.invoice', 'Invoice', readonly=True, select=True),
        'line_id':fields.many2one('account.invoice.line', 'Linea', readonly=True, select=True),
    }
    
    _rec_name = 'date'
    
    
    def init(self,cr):
        drop_view_if_exists(cr,'report_cost')
        cr.execute('''
            create or replace view report_cost as (
            select
                invo.date_invoice as date,
                line.id as id,
                line.product_id as product_id,
                invo.type as type_inv,
                case when invo.type='out_refund'
                    then
                        0.0
                    else
                        case when invo.type='in_invoice'
                            then
                                line.price_unit
                            else
                                case when invo.type='in_refund'
                                    then
                                        line.price_unit*(-1)
                                    else
                                        0.0
                                end 
                        end    
                end as last_cost,
                line.uos_id as uom_id,
                case when invo.type='out_refund'
                    then
                        line.price_unit*(-1)
                    else
                        case when invo.type='in_invoice'
                            then 
                                0.0
                            else
                                line.price_unit
                        end
                end as price_unit
            from account_invoice invo
                inner join account_invoice_line line on (invo.id=line.invoice_id)
            where invo.state in ('open','paid')
        )''')
     
report_cost()


