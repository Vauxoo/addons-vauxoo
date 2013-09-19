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
from openerp.osv import osv, fields
import decimal_precision as dp
from openerp.tools.translate import _


class mrp_consume(osv.TransientModel):
    _inherit = 'mrp.consume'

    def _get_default_wo_lot(self, cr, uid, context=None):
        """
        @return: The first Work Order Lot to produce (cardinal order).
        """
        context = context or {}
        res = False
        production_obj = self.pool.get('mrp.production')
        active_id = context.get('active_id', False)
        active_model = context.get('active_model', False)
        if active_id:
            if active_model == 'mrp.production':
                production_id = active_id
                wol_brws = production_obj.browse(
                    cr, uid, production_id, context=context).wo_lot_ids
                res = [wol_brw.id
                       for wol_brw in wol_brws
                       if wol_brw.state == 'draft']
            elif active_model == 'mrp.workorder.lot':
                res = [active_id]
            else:
                raise osv.except_osv (
                    _('Error!!'),
                    _('This wizard only can be call from the manufacturing'
                      ' order form or the Work Orders by Active Lot menu.'))

        #~ raise osv.except_osv ('stop', 'here')

        return res and res[0] or False

    def _get_default_mo_id(self, cr, uid, context=None):
        """
        Return the production id.
        """
        context = context or {}
        wol_obj = self.pool.get('mrp.workorder.lot')
        res = False
        active_id = context.get('active_id', False)
        active_model = context.get('active_model', False)
        if active_id:
            if active_model == 'mrp.production':
                res = active_id
            elif active_model == 'mrp.workorder.lot':
                res = wol_obj.browse(
                    cr, uid, active_id, context=context).production_id.id
            else:
                raise osv.except_osv (
                    _('Error!!'),
                    _('This wizard only can be call from the manufacturing'
                      ' order form or the Work Orders by Active Lot menu.'))
        return res

    _columns = {
        'production_id': fields.many2one(
            'mrp.production',
            string=_('Manufacturing Order'),
            help=_('Manufacturing Order')),
        'wo_lot_id': fields.many2one(
            'mrp.workorder.lot',
            required=True,
            string=_('Work Orders Lots'),
            help=_('Work Orders Lots.')),
    }

    _defaults = {
        'production_id': _get_default_mo_id,
        'wo_lot_id': _get_default_wo_lot,
    }

    def onchange_wo_lot_ids(self, cr, uid, ids, production_id, wo_lot_id,
                            consume_line_ids, context=None):
        """
        Loads product information from the work order selected.
        @param production_id: manufacturing order id.
        @param wo_lot_id: selected work order lot.
        @param consume_line_ids: current cosumne product lines.
        """

        context = context or {}
        values = []
        production = self.pool.get('mrp.production').browse(
            cr, uid, production_id, context=context)
        wo_lot_obj = self.pool.get('mrp.workorder.lot')

        if wo_lot_id:
            wo_lot = wo_lot_obj.browse(cr, uid, wo_lot_id, context=context)
            #~ extract move data for products
            move_d = {}

            if production.move_lines:
                for move in production.move_lines:
                    move_d[move.product_id.id] = {
                        'move_id': move.id,
                        'location_id': move.location_id.id,
                        'location_dest_id': move.location_dest_id.id,
                        }
            else:
                raise osv.except_osv(
                    _('Error!'),
                    _('You have not more Product to Consume, please add new'
                      ' lines by clicking the Product Request/Return Button.'))
            #~ create consume lines
            for product_line in production.product_lines:
                product_id = product_line.product_id.id
                values += [{
                    'product_id': product_id,
                    'quantity':
                    product_line.product_qty * wo_lot.percentage/100.0,
                    'product_uom': product_line.product_uom.id,
                    'move_id': move_d[product_id]['move_id'],
                    'location_id': move_d[product_id]['location_id'],
                    'location_dest_id': move_d[product_id]['location_dest_id']
                }]

        return {'value': {'consume_line_ids': values}}

    def action_active_lot(self, cr, uid, ids, context=None):
        """
        Active Work Order Lot
        """
        context = context or {}
        wol_obj = self.pool.get('mrp.workorder.lot')
        consume = self.browse(cr, uid, ids, context=context)[0]
        wol_obj.write(cr, uid, consume.wo_lot_id.id,
                      {'state': 'picking'}, context=context)
        return True

    def action_consume(self, cr, uid, ids, context=None):
        """
        Overwrite action_consume() method to change the work order lot state
        from picking to open state.
        """
        context = context or {}
        wol_obj = self.pool.get('mrp.workorder.lot')
        res = super(mrp_consume, self).action_consume(
            cr, uid, ids, context=context)
        if context.get('active_model', False) == 'mrp.workorder.lot':
            wol_id = context.get('active_id', False)
            if wol_id:
                wol_obj.write(cr, uid, wol_id, {'state': 'open'},
                              context=context)
            else:
                raise osv.except_osv(
                    _('Error!'),
                    _('No valid operation. no work order lot active_id.')
                )

        #~ refresh kaban view
        ir_obj = self.pool.get('ir.model.data')
        dummy, view_id = ir_obj.get_object_reference(
            cr, uid, 'mrp_byworkcenter_capacity',
            'mrp_workorder_lot_kanban_view')

        dummy, search_view_id = ir_obj.get_object_reference(
            cr, uid, 'mrp_byworkcenter_capacity',
            'mrp_wol_search_view')

        dummy, action_window_id = ir_obj.get_object_reference(
            cr, uid, 'mrp_byworkcenter_capacity',
            'mrp_wol_picking_kanban_action')
        act_obj = self.pool.get('ir.actions.act_window')

        return {
            'view_id': view_id,
            'view_type': 'form',
            'view_mode': 'kanban',
            'views': [(view_id, 'kanban')],
            'search_view_id': search_view_id,
            'res_model': 'mrp.workorder.lot',
            'type': 'ir.actions.act_window',
            'target': 'inlineview',
            'context': {'search_default_wol_picking': True},
            'help': act_obj.browse(cr, uid, action_window_id,
                                   context=context).help
        }



class mrp_produce(osv.TransientModel):
    _inherit = 'mrp.produce'

    def _get_default_mo_id(self, cr, uid, context=None):
        """
        Return the production id.
        """
        context = context or {}
        wol_obj = self.pool.get('mrp.workorder.lot')
        res = False
        active_id = context.get('active_id', False)
        active_model = context.get('active_model', False)
        if active_id:
            if active_model == 'mrp.production':
                res = active_id
            elif active_model == 'mrp.workorder.lot':
                res = wol_obj.browse(
                    cr, uid, active_id, context=context).production_id.id
            else:
                raise osv.except_osv (
                    _('Error!!'),
                    _('This wizard only can be call from the manufacturing'
                      ' order form or the Work Orders by Active Lot menu.'))
        return res

    def _get_default_wo_lot(self, cr, uid, context=None):
        """
        @return: The first Work Order Lot ready to Produce (cardinal order).
        """
        context = context or {}
        production_obj = self.pool.get('mrp.production')
        active_id = context.get('active_id', False)
        active_model = context.get('active_model', False)
        if active_id:
            if active_model == 'mrp.production':
                production_id = active_id
                wol_brws = production_obj.browse(
                    cr, uid, production_id, context=context).wo_lot_ids
                res = [wol_brw.id
                       for wol_brw in wol_brws
                       if wol_brw.state == 'ready']
            elif active_model == 'mrp.workorder.lot':
                res = [active_id]
            else:
                raise osv.except_osv (
                    _('Error!!'),
                    _('This wizard only can be call from the manufacturing'
                      ' order form or the Work Orders by Active Lot menu.'))

        if not res:
            raise osv.except_osv (
                _('Warning!!'),
                _('You can Produce because you have not Ready to Finish Work'
                  ' Order Lots.'))

        return res and res[0] or False

    _columns = {
        'production_id': fields.many2one(
            'mrp.production',
            string=_('Manufacturing Order'),
            help=_('Manufacturing Order')),
        'wo_lot_id': fields.many2one(
            'mrp.workorder.lot',
            required=True,
            string=_('Work Orders Lots'),
            help=_('Work Orders Lots.')),
    }

    _defaults = {
        'production_id': _get_default_mo_id,
        'wo_lot_id': _get_default_wo_lot,
    }

    def action_produce(self, cr, uid, ids, context=None):
        """
        Overwrite the action_produce() method to set the Work Order Lot to
        Done state when the lot is produced and also add the serial number to
        produced products moves created.
        """
        context = context or {}
        wol_obj = self.pool.get('mrp.workorder.lot')
        sm_obj = self.pool.get('stock.move')
        #~ create convencianal moves
        for produce in self.browse(cr, uid, ids, context=context):
            res = super(mrp_produce, self).action_produce(
                cr, uid, ids, context=context)
        #~ add the serial number to the moves
        for produce in self.browse(cr, uid, ids, context=context):
            prodlot_id = dict(
                [(produce_line.product_id.id, produce_line.prodlot_id.id)
                 for produce_line in produce.produce_line_ids])
            for move in produce.production_id.move_created_ids2:
                sm_obj.write(
                    cr, uid, move.id,
                    {'prodlot_id': prodlot_id[move.product_id.id]},
                    context=context)
        #~ set work order lot to done
        wol_obj.write(cr, uid, produce.wo_lot_id.id, {'state': 'done'},
                      context=context)
        return res

class mrp_produce_line(osv.TransientModel):
    _inherit = 'mrp.produce.line'

    _columns = {
        'prodlot_id': fields.many2one(
            'stock.production.lot',
            _('Serial Number'),
            help=_('Production Serial Number for Production Lot.')
        ),
    }
