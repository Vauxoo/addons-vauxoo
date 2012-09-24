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
import time
from osv import osv, fields
import decimal_precision as dp
from tools.translate import _

class mrp_request_return(osv.osv_memory):
    _name='mrp.request.return'
    _columns={
        're_line_ids' : fields.one2many('mrp.request.return.line','wizard_id','Acreation'),
        'type' : fields.selection([('request','Request'),('return','Return')], 'Type', required=True)
    }
    def action_request_return(self, cr, uid, ids, context={}):
        stock_picking = self.pool.get('stock.picking')
        mrp_prouction = self.pool.get('mrp.production')
        
        mrp_ids = context.get('active_ids', [])
        production = self.pool.get('mrp.production').browse(cr, uid, mrp_ids, context=context)[0]
        
        for wizard_moves  in self.browse(cr, uid, ids, context=context):
            pick_id = mrp_prouction._make_production_internal_shipment(cr, uid, production, context=context)
            for wiz_move in wizard_moves.re_line_ids:
                if wiz_move.product_qty > 0.0:
                    shipment_move_id = mrp_prouction._make_production_internal_shipment_line(cr, uid, wiz_move, pick_id, False)
            
        return True
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(mrp_request_return, self).default_get(cr, uid, fields, context=context)
        mrp_ids = context.get('active_ids', [])
        if not mrp_ids or (not context.get('active_model') == 'mrp.production') \
            or len(mrp_ids) != 1:
            return res
        mrp_id, = mrp_ids
        if 're_line_ids' in fields:
            mrp = self.pool.get('mrp.production').browse(cr, uid, mrp_id, context=context)
            moves = [self._partial_move_for(cr, uid, m, mrp) for m in mrp.product_lines]
            res.update(re_line_ids=moves)
        return res

    def _partial_move_for(self, cr, uid, move, production):
        partial_move = {
            'product_id' : move.product_id.id,
            'product_qty' : 0.0,
            'product_uom' : move.product_uom.id,
            'product_uos_qty': move.product_uos and move.product_uos_qty or False,
            'product_uos': move.product_uos and move.product_uos.id or False,
            'location_id' : production.location_src_id.id,
            'location_dest_id' : production.location_src_id.id,
            'production_id' : move.production_id.id
        }
        return partial_move
mrp_request_return()


class mrp_request_return_line(osv.osv_memory):
    _name='mrp.request.return.line'
    _rec_name = 'product_id'
    _columns = {
        'product_id' : fields.many2one('product.product', string="Product", required=True),
        'product_qty' : fields.float("Quantity", digits_compute=dp.get_precision('Product UoM'), required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', required=True,),
        'location_id': fields.many2one('stock.location', 'Location', required=True),
        'location_dest_id': fields.many2one('stock.location', 'Dest. Location', required=True),
        'move_id' : fields.many2one('stock.move', "Move"),
        'production_id' :fields.many2one('mrp.production','Production'),
        'product_uos': fields.many2one('product.uom', 'Product UOS'),
        'product_uos_qty' : fields.float('Quantity UoS'),
        'wizard_id' : fields.many2one('mrp.request.return', string="Wizard"),
    }

mrp_request_return_line()

