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
        """
        La función def _get_product_subproduction_qty, recibirá el product_id que deberá
        contabilizar de materia prima, para saber que producto es el que se está consumiendo.
        Y este contexto, se le mandará, con el producto_terminado de la producción padre, y
        calculará cuánto se consumió en realidad en la producción hija como materia prima.
        """
        if context is None:
            context = {}
        result = {}
        subp_sum = 0.0
        subp_real_sum = 0.0
        for production in self.browse(cr, uid, ids, context=context):
            if production.subproduction_ids:
                for subprod in production.subproduction_ids:
                    if subprod.product_lines:
                        for scheduled in subprod.product_lines:
                            if scheduled.product_id.id == production.product_id.id:
                                subp_sum += scheduled.product_qty
                                
                    if subprod.move_lines2:
                        for consumed in subprod.move_lines2:
                            if (consumed.product_id.id == production.product_id.id and consumed.state not in ('cancel')):
                                subp_real_sum += consumed.product_qty
            result[production.id] = {
                'product_subproduction_qty_real': subp_real_sum,
                'product_subproduction_qty_planned': subp_sum
            }
        return result
    
    _columns = {
        'parent_id': fields.many2one('mrp.production', 'Parent production'),
        'subproduction_ids': fields.one2many('mrp.production', 'parent_id', 'Subproductions'),
        'product_subproduction_qty_real': fields.function(_get_product_subproduction_qty, type='float', method=True, string='Really used', multi=True),
        'product_subproduction_qty_planned': fields.function(_get_product_subproduction_qty, type='float', method=True, string='Planned', multi=True),
    }

mrp_production()