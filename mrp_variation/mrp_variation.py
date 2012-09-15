# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
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
from osv import osv,fields

class mrp_production(osv.osv):
    _inherit='mrp.production'
    
    _columns = {
        'variation_ids' : fields.one2many('mrp.variation','production_id','Variation Product'),
    }

mrp_production()

class mrp_variation(osv.osv):
    _name='mrp.variation'
    _rec_name='product_id'
    
    _columns = {
        'product_id' : fields.many2one('product.product','Product'),
        'quantity' : fields.float('quantity'),
        'production_id' : fields.many2one('mrp.production','production'),
        'product_uom' : fields.many2one('product.uom','UoM')
    }
    
mrp_variation()

class mrp_production(osv.osv):
    _inherit='mrp.production'
    
    def action_finish(self,cr,uid,ids,context={}):
        res = super(mrp_production, self).action_finish(cr,uid,ids,context=context)
        self.create_variation(cr,uid,ids,context=context)
        return res
    
    def create_consume_real(self,cr,uid,ids,context={}):
        product_product=self.pool.get('product.product')
        for production in self.browse(cr,uid,ids,context=context):
            cr.execute("""
                    SELECT sm.product_uom,sm.product_id,sum(COALESCE(sm.product_qty,0)) AS product_qty
                        FROM mrp_production_move_ids mpmi JOIN stock_move sm
                        ON sm.id=mpmi.move_id
                    WHERE mpmi.production_id=%s
                    AND sm.state='done'
                    GROUP BY sm.product_id,sm.product_uom 
                    """,(production.id,))
            dat = cr.dictfetchall()
            res_real={}
            for lin in dat:
                res_real.setdefault(lin['product_id'],0)
                product=product_product.browse(cr,uid,lin['product_id'],context=context)
                qty_uom_convert=self.pool.get('product.uom')._compute_qty(cr, uid, lin['product_uom'], lin['product_qty'], to_uom_id=product.uom_id.id)
                res_real[lin['product_id']]+=qty_uom_convert
        return res_real
    
    def create_consume_planned(self,cr,uid,ids,context={}):
        product_product=self.pool.get('product.product')
        for production in self.browse(cr,uid,ids,context=context):
            cr.execute("""
                    SELECT product_id,sum(COALESCE(product_qty,0)) AS product_qty,product_uom
                        FROM mrp_production_product_line
                    WHERE production_id=%s
                    GROUP BY product_id,product_uom
                    """,(production.id,))
            dat = cr.dictfetchall()
            res_planned={}
            for lin in dat:
                res_planned.setdefault(lin['product_id'],0)
                product=product_product.browse(cr,uid,lin['product_id'],context=context)
                qty_uom_convert=self.pool.get('product.uom')._compute_qty(cr, uid, lin['product_uom'], lin['product_qty'], to_uom_id=product.uom_id.id)
                res_planned[lin['product_id']]+=qty_uom_convert
        return res_planned
    
    def create_variation(self,cr,uid,ids,context={}):
        prod_variation = self.pool.get('mrp.variation')
        prod_product = self.pool.get('product.product')
        for production in self.browse(cr,uid,ids,context=context):
            prod_variation.unlink(cr,uid,map(lambda x:x.id, production.variation_ids))
            real=self.create_consume_real(cr,uid,ids,context=context)
            planned=self.create_consume_planned(cr,uid,ids,context=context)
            lista=[]
            lista.extend(real.keys())
            lista.extend(planned.keys())
            lista=list(set(lista))
            res_diff = dict( planned )
            for product_id in lista:
                res_diff[product_id]-=real.get(product_id, 0)
            for val_diff in res_diff.items():
                prod_variation.create(cr,uid,{'product_id':val_diff[0],
                    'quantity':(val_diff[1])*-1,
                    'product_uom':prod_product.browse(cr,uid,val_diff[0]).uom_id.id,
                    'production_id':production.id
                    })
        return True

mrp_production()

