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
from osv import osv, fields
import decimal_precision as dp
import time

class wizard_production_make(osv.osv_memory):
    _name='wizard.production.make'
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'product_qty': fields.float('Product Qty', digits_compute=dp.get_precision('Product UoM'), required=True, states={'draft':[('readonly',False)]}, readonly=True),
        'product_uom': fields.many2one('product.uom', 'Product UOM', required=True, states={'draft':[('readonly',False)]}, readonly=True),
        'date_planned': fields.datetime('Scheduled date', required=True, select=1),
        'move_created_ids': fields.one2many('stock.move', 'production_id', 'Products to Produce', domain=[('state','not in', ('done', 'cancel'))], states={'done':[('readonly',True)]}),
    }
    _defaults = {
        'date_planned': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'), 
    }
    
    def onchange_product_id(self, cr, uid, ids, product_id, name, context=None):
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            return {'value': {'name': prod.name, 'product_uom': prod.uom_id.id}}
        return {}
        
    def action_add_production(self, cr, uid, ids, context=None):
        production_obj=self.pool.get('mrp.production')
        new_production_obj=self.pool.get('wizard.production.make')
        product=new_production_obj.browse(cr, uid, ids, context=context)[0]
        production_obj.create(cr, uid, {
            'product_id': product.product_id.id,
            'product_qty': product.product_qty,
            'product_uom': product.product_uom.id,
            'date_planned': product.date_planned ,
            'location_src_id':'12' ,
            'location_dest_id':'11' ,
            'move_created_ids':product.move_created_ids ,
            #~ 'prodlot_id': ,
                })
        return ''
        
wizard_production_make()
        
