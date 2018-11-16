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
from openerp.osv import osv, fields
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
                raise osv.except_osv(
                    _('Error!!'),
                    _('This wizard only can be call from the manufacturing'
                      ' order form or the Work Orders by Active Lot menu.'))

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
                raise osv.except_osv(
                    _('Error!!'),
                    _('This wizard only can be call from the manufacturing'
                      ' order form or the Work Orders by Active Lot menu.'))
        return res

    _columns = {
        'production_id': fields.many2one(
            'mrp.production',
            string='Manufacturing Order',
            help='Manufacturing Order'),
        'wo_lot_id': fields.many2one(
            'mrp.workorder.lot',
            required=True,
            string='Work Orders Lots',
            help='Work Orders Lots.'),
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
        consume_line_list = list()
        production_obj = self.pool.get('mrp.production')
        production_brw = production_obj.browse(
            cr, uid, production_id, context=context)

        if wo_lot_id:
            if not production_brw.move_lines:
                raise osv.except_osv(
                    _('Error!'),
                    _('You have not more Product to Consume, please add new'
                      ' lines by clicking the Product Request/Return Button.'))
            consume_line_list = self._get_consume_line_list_with_wol_percent(
                cr, uid, production_id, wo_lot_id, context=context)
        return {'value': {'consume_line_ids': consume_line_list}}

    def _get_consume_line_list_with_wol_percent(self, cr, uid, production_id,
                                                wo_lot_id, context=None):
        """
        Get a list of consume lines to create with a modification of the
        product qty with work order lot related percentage.
        @param production_id: manufacturing order id.
        @param wo_lot_id: work order lot id.
        @return: a list of consume lines to create.
        """
        context = context or {}
        production_obj = self.pool.get('mrp.production')
        wol_obj = self.pool.get('mrp.workorder.lot')
        production_brw = production_obj.browse(
            cr, uid, production_id, context=context)
        wol_brw = wol_obj.browse(cr, uid, wo_lot_id, context=context)
        consume_line_list = self._get_consume_lines_list(
            cr, uid, production_id, context=context)
        sheduled_qty = dict(set(
            [(product_line.product_id.id, product_line.product_qty)
             for product_line in production_brw.product_lines]
        ))
        for consume_line in consume_line_list:
            consume_line.update({
                'quantity': sheduled_qty[consume_line['product_id']]
                * wol_brw.percentage / 100.0})
        return consume_line_list

    def action_active_lot(self, cr, uid, ids, context=None):
        """
        Get the work order lot in the consume wizard and update its state
        to picking state.
        @return: True
        """
        context = context or {}
        wol_obj = self.pool.get('mrp.workorder.lot')
        consume = self.browse(cr, uid, ids, context=context)[0]
        wol_obj.write(cr, uid, consume.wo_lot_id.id,
                      {'state': 'picking'}, context=context)
        return True

    def action_consume(self, cr, uid, ids, lot_id=False, context=None):
        """
        Overwrite action_consume() method to change the work order lot state
        from picking to open state.
        """
        context = context or {}
        wol_obj = self.pool.get('mrp.workorder.lot')
        res = super(mrp_consume, self).action_consume(
            cr, uid, ids, lot_id=lot_id, context=context)
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
        view_id, search_view_id, action_help = \
            self._get_kanban_view_data(cr, uid, context=context)

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
            'help': action_help
        }

    def _get_kanban_view_data(self, cr, uid, context=None):
        """
        @return: a tuple (view_id, search_view_id, action_help)
        related to the kaban view for ready to picking work order lots.
        """
        context = context or {}
        ir_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        module_name = 'mrp_workorder_lot'
        dummy, view_id = ir_obj.get_object_reference(
            cr, uid, module_name, 'mrp_workorder_lot_kanban_view')
        dummy, search_view_id = ir_obj.get_object_reference(
            cr, uid, module_name, 'mrp_wol_search_view')
        dummy, action_window_id = ir_obj.get_object_reference(
            cr, uid, module_name, 'mrp_wol_picking_kanban_action')

        action_help = act_obj.browse(
            cr, uid, action_window_id, context=context).help

        return (view_id, search_view_id, action_help)


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
                raise osv.except_osv(
                    _('Error!!'),
                    _('This wizard only can be call from the manufacturing'
                      ' order form or the Work Orders by Active Lot menu.'))
        return res

    def _get_default_wo_lot(self, cr, uid, context=None):
        """
        @return: The first Work Order Lot ready to Produce (cardinal order).
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
                       if wol_brw.state == 'ready']
            elif active_model == 'mrp.workorder.lot':
                res = [active_id]
            else:
                raise osv.except_osv(
                    _('Error!!'),
                    _('This wizard only can be call from the manufacturing'
                      ' order form or the Work Orders by Active Lot menu.'))

            if not res:
                raise osv.except_osv(
                    _('Warning!!'),
                    _('You can Produce because you have not Ready to Finish'
                      ' Work Order Lots.'))

        return res and res[0] or False

    _columns = {
        'production_id': fields.many2one(
            'mrp.production',
            string='Manufacturing Order',
            help='Manufacturing Order'),
        'wo_lot_id': fields.many2one(
            'mrp.workorder.lot',
            required=True,
            string='Work Orders Lots',
            help='Work Orders Lots.'),
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

    def _get_produce_line_prodlot_id(self, cr, uid, product_id, context=None):
        """
        Return the first production lot id found for the given product.
        @param product_id: product id.
        """
        # Note: First my intention was to use the move_brw.prodlot_id to get
        # the prodlot_id but this field is not set, I imagine that is set
        # before the move is consumed.
        context = context or {}
        prodlot_obj = self.pool.get('stock.production.lot')
        prodlot_ids = \
            prodlot_obj.search(
                cr, uid, [('product_id', '=', product_id)], context=context) \
            or False
        return prodlot_ids and prodlot_ids[0] or False

    def _get_produce_line_values(self, cr, uid, move_id, context=None):
        """
        return the dictionary that fill the produce lines with the move values.
        @param move_id: move id.
        """
        context = context or {}
        res = super(mrp_produce, self)._get_produce_line_values(
            cr, uid, move_id, context=context)
        res.update({'prodlot_id': self._get_produce_line_prodlot_id(
            cr, uid, res['product_id'], context=context)})
        return res


class mrp_produce_line(osv.TransientModel):
    _inherit = 'mrp.produce.line'

    _columns = {
        'prodlot_id': fields.many2one(
            'stock.production.lot',
            'Serial Number',
            help='Production Serial Number for Production Lot.'),
    }
