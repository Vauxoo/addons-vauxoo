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
    
    def action_compute(self, cr, uid, ids, properties=[], context=None):
        mrp_pt = self.pool.get('mrp.pt.planified')
        bom_obj = self.pool.get('mrp.bom')
        res = super(mrp_production, self).action_compute(cr,uid,ids,properties=properties,context=context)
        for production in self.browse(cr,uid,ids,context=context):
            bom_point = production.bom_id
            bom_id = production.bom_id.id
            if not bom_point:
                bom_id = bom_obj._bom_find(cr, uid, production.product_id.id, production.product_uom.id, properties)
                    
            if not bom_id:
                raise osv.except_osv(_('Error'), _("Couldn't find a bill of material for this product."))
            
            for subpro in bom_obj.browse(cr,uid,[bom_id]):
                for pro in subpro.sub_products:
                    val = {
                        'product_id' : pro.product_id and pro.product_id.id or False,
                        'quantity' : pro.product_qty,
                        'product_uom' : pro.product_uom.id,
                        'production_id' : production.id
                    }
                    mrp_pt.create(cr,uid,val)

            for bom in bom_obj.browse(cr,uid,[bom_id]):
                for bom_line in bom.bom_lines:
                    if bom_line.type == 'phantom' and not bom_line.bom_lines:
                        newbom = bom_obj._bom_find(cr, uid, bom_line.product_id.id, bom_line.product_uom.id, properties)
                        if newbom:
                            bom2 = bom_obj.browse(cr, uid, newbom, context=context)
                            for sub_product in bom2.sub_products:
                                val = {
                                    'product_id' : sub_product.product_id and sub_product.product_id.id or False,
                                    'quantity' : sub_product.product_qty,
                                    'product_uom' : sub_product.product_uom.id,
                                    'production_id' : production.id
                                }
                                mrp_pt.create(cr,uid,val)
                            
        return res
mrp_production()

