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

dicc = {}

class sale_order_line(osv.osv):
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False,context=None):
        global dicc
        if context is None:
            context ={}
        module = self.pool.get('ir.module.module')
        res = super(sale_order_line,self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag)
        
        if dicc.get('stop',False):
            res['value'].get('price_unit',False) and res['value'].pop('price_unit')
        
        if dicc.get('price_unit',False):
            dicc = {}
            res['value'].pop('price_unit')
            res.update({'stop':True})
        
        if 'price_unit' in res.get('value'):
            dicc = {}
            
        else:
            dicc.update({'stop':True})
        
        return res
    
    
    def price_unit(self,cr,uid,ids,price_method,product_uom,qty,context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        global dicc
        dicc = {}
        if price_method and product_uom:
            price_obj = self.pool.get('method.price')
            uom_obj = self.pool.get('product.uom')
            uom_brw = uom_obj.browse(cr,uid,product_uom,context=context)
            price_brw = price_obj.browse(cr,uid,price_method,context=context)
            price = price_brw and price_brw.unit_price
            price = uom_obj._compute_price(cr, uid, product_uom, price, to_uom_id=False)
            
            e = uom_obj._compute_qty(cr, uid, product_uom, qty, to_uom_id=product_uom)
            print "price",price
            #~ if uom_brw.uom_type == 'bigger':
                #~ price = price_brw.unit_price * uom_brw.factor_inv
            #~ elif uom_brw.uom_type == 'smaller':
                #~ price = price_brw.unit_price / uom_brw.factor_inv
            res['value'].update({'price_unit': price})
            dicc.update({'price_unit':True})
        return res
    
    _inherit = 'sale.order.line'
    _columns = {
   
    'price_structure_id':fields.many2one('method.price','Select Price'),
    
    }
    
sale_order_line()



