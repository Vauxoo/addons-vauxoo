# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: fernandoL (fernando_ld@vauxoo.com)
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

from tools.translate import _
from osv import osv, fields
import decimal_precision as dp

class mrp_production(osv.osv):
    _inherit = "mrp.production"
    
    def _get_product_subproduction_qty(self, cr, uid, ids, field_names, args, context=None):
        if context is None:
            context = {}
        product_uom_pool=self.pool.get('product.uom')
        result = {}
        subp_sum = 0.0
        subp_real_sum = 0.0
        for production in self.browse(cr, uid, ids, context=context):
            if production.subproduction_ids:
                for subprod in production.subproduction_ids:
                    if subprod.product_lines:
                        for scheduled in subprod.product_lines:
                            if scheduled.product_id.id == production.product_id.id:
                                subp_sum += product_uom_pool._compute_qty(cr, uid, scheduled.product_uom.id, scheduled.product_qty, to_uom_id=production.product_uom.id)
                                
                    if subprod.move_lines2:
                        for consumed in subprod.move_lines2:
                            if (consumed.product_id.id == production.product_id.id and consumed.state not in ('cancel')):
                                subp_real_sum += product_uom_pool._compute_qty(cr, uid, consumed.product_uom.id, consumed.product_qty, to_uom_id=production.product_uom.id)
            result[production.id] = {
                'product_subproduction_qty_real': subp_real_sum,
                'product_subproduction_qty_planned': subp_sum
            }
        return result
    
    def _get_parent_product(self, cr, uid, ids, field_names, args, context=None):
        product_uom_pool=self.pool.get('product.uom')
        parent_id = context.get('subproduction_parent_id') or 0
        parent_product_id = 0
        result = {}
        if parent_id:
            parent_production = self.browse(cr, uid, parent_id, context=context)
            parent_product_id = parent_production.product_id.id
        
        for production in self.browse(cr, uid, ids, context=context):
            planned_qty = 0.0
            real_qty = 0.0
            if production.product_lines:
                for scheduled in production.product_lines:
                    if scheduled.product_id.id == parent_product_id:
                        planned_qty += product_uom_pool._compute_qty(cr, uid, scheduled.product_uom.id, scheduled.product_qty, to_uom_id=parent_production.product_uom.id)
                        
            if production.move_lines2:
                for consumed in production.move_lines2:
                    if (consumed.product_id.id == parent_product_id and consumed.state in ('done')):
                        real_qty += product_uom_pool._compute_qty(cr, uid, consumed.product_uom.id, consumed.product_qty, to_uom_id=parent_production.product_uom.id)
            
            result[production.id] = {
                'product_subproduction_qty_line_real': real_qty,
                'product_subproduction_qty_line_planned': planned_qty
            }
        return result
        
    _columns = {
        'subproduction_ids': fields.many2many('mrp.production', 'rel_mrp_subproduction_self', 'parent_id', 'children_id', 'Subproductions'),
        'product_subproduction_qty_real': fields.function(_get_product_subproduction_qty, type='float', method=True, string='Really used', multi=True, help="UoM is the same that the parent production order"),
        'product_subproduction_qty_planned': fields.function(_get_product_subproduction_qty, type='float', method=True, string='Planned', multi=True, help="UoM is the same that the parent production order"),
        'product_subproduction_qty_line_real': fields.function(_get_parent_product, type='float', method=True, string='Real in line', multi=True),
        'product_subproduction_qty_line_planned': fields.function(_get_parent_product, type='float', method=True, string='Planned in line', multi=True),
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'subproduction_ids' : [],
        })
        return super(mrp_production, self).copy(cr, uid, id, default, context)

mrp_production()