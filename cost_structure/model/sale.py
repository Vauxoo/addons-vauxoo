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


class sale_order_line(osv.osv):
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False,context=None):
        global dicc
        if context is None:
            context ={}
        product_obj = self.pool.get('product.product')
        product_brw = product and product_obj.browse(cr,uid,product,context=context)
        res = super(sale_order_line,self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag)
        
        res.get('value',False) and res.get('value',False).update({'cost_structure_id':product_brw and product_brw.property_cost_structure and product_brw.property_cost_structure.id })
        res.get('value',False) and 'price_unit' in res.get('value',False)  and res['value'].pop('price_unit') 
        return res
    
    
    def price_unit(self,cr,uid,ids,price_method,product_uom,qty,context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        
        if price_method and product_uom:
            price_obj = self.pool.get('method.price')
            uom_obj = self.pool.get('product.uom')
            uom_brw = uom_obj.browse(cr,uid,product_uom,context=context)
            price_brw = price_obj.browse(cr,uid,price_method,context=context)
            price = price_brw and price_brw.unit_price
            price = uom_obj._compute_price(cr, uid, product_uom, price, to_uom_id=False)
            
            e = uom_obj._compute_qty(cr, uid, product_uom, qty, to_uom_id=product_uom)
            res['value'].update({'price_unit': price})
        return res
    
    _inherit = 'sale.order.line'
    _columns = {
        'price_structure_id':fields.many2one('method.price','Select Price'),
        'cost_structure_id':fields.many2one('cost.structure','Cost Structure'),
    
    }
    
sale_order_line()

class sale_order(osv.osv):
   
   
    
    _inherit = 'sale.order'
    
        
    def _price_status(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        if len(ids) == 0:
            return {}
        res = {}
        product = []
        cost_obj = self.pool.get('cost.structure')
        for order in self.browse(cr,uid,ids,context=context):
            for line in order.order_line:
                property_cost_structure = line and line.product_id and line.product_id.property_cost_structure and line.product_id.property_cost_structure.id or False
                if property_cost_structure and len(line.product_id.method_cost_ids) == len([i.id for i in line.product_id.method_cost_ids if line.price_unit < i.unit_price]):
                    product.append(u'Intenta vender el producto %s a un precio menor al estimado para su venta'%line.product_id.name)
                    res[order.id] = {'status_bool':True}
                
                elif property_cost_structure and len(line.product_id.method_cost_ids) == len([i.id for i in line.product_id.method_cost_ids if line.price_unit > i.unit_price]):
                    product.append(u'Intenta vender el producto %s a un precio mayor al estimado para su venta'%line.product_id.name)
                    res[order.id] = {'status_bool':True}
                
                
                elif not property_cost_structure:
                    product.append(u'El producto %s no tiene una estructura de costo'%line.product_id.name)
                    res[order.id] = {'status_bool':True}
            
            if product:
                res[order.id] = '\n'.join(product)            
            else:
                res[order.id] = {'status_bool':False}
                product = []
                res[order.id] = '\n'.join(product)  
                
        return res
        
        
    _columns = {
    
        'status_price':fields.function(_price_status, method=True,type="text", store=True, string='Status Price'),
        'status_bool':fields.function(_price_status, method=True,type="boolean", string='Status Price'),
        
        
    }
    
    _defaults = {
    'status_bool':False
    
    
    }
    def price_unit_confirm(self,cr,uid,ids,context=None):
        if context is None:
            context = {}
        product = []
        sale_brw = self.browse(cr,uid,ids and ids[0],context=context)
        for line in sale_brw.order_line:
            property_cost_structure = line and line.product_id and line.product_id.property_cost_structure and line.product_id.property_cost_structure.id or False
            if property_cost_structure and len(line.product_id.method_cost_ids) == len([i.id for i in line.product_id.method_cost_ids if line.price_unit < i.unit_price]):
                product.append(u'Intenta vender el producto %s a un precio menor al estimado para su venta'%line.product_id.name)
        
            elif property_cost_structure and len(line.product_id.method_cost_ids) == len([i.id for i in line.product_id.method_cost_ids if line.price_unit > i.unit_price]):
                product.append(u'Intenta vender el producto %s a un precio mayor al estimado para su venta'%line.product_id.name)


            elif not property_cost_structure:
                product.append(u'The product %s has not a cost structure'%line.product_id.name)
                    
        if len(product) > 0:
            raise osv.except_osv(_('Error'), _('\n'.join(product)))
       
        return True
    
    
sale_order()


