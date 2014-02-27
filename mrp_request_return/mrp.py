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


class mrp_production(osv.Model):
    _inherit = 'mrp.production'

    _columns = {
        'picking_ids': fields.one2many('stock.picking', 'production_id',
            'Picking')
    }

    def action_finished_consume(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        stock_picking = self.pool.get('stock.picking')
        mrp_production2 = self.pool.get('mrp.production')
        stock_move = self.pool.get('stock.move')
        production = self.pool.get('mrp.production').browse(
            cr, uid, ids, context=context)[0]

        for wizard_moves in self.browse(cr, uid, ids, context=context):
            context['type'] = 'return'
            pick_id_return = mrp_production2._make_production_internal_shipment2(
                cr, uid, production, context=context)
            stock_picking.write(cr, uid, pick_id_return, {
                                'state': 'draft',
                                'auto_picking': False,
                                'production_id': production.id})
            for wiz_move2 in wizard_moves.move_lines:
                if wiz_move2.product_qty > 0.0:
                    shipment_move_id = mrp_production2._make_production_internal_shipment_line2(
                        cr, uid, production, wiz_move2, pick_id_return,
                        parent_move_id=False, destination_location_id=False)
                    stock_move.write(cr, uid, shipment_move_id, {
                                     'state': 'draft'})
        res = super(mrp_production, self).action_finished_consume(
            cr, uid, ids, context=context)
        return res

    def _make_production_internal_shipment_line2(self, cr, uid, production,
                                                production_line, shipment_id,
                                                parent_move_id,
                                                destination_location_id=False,
                                                context=None):
        stock_move = self.pool.get('stock.move')
        date_planned = production.date_planned
        if production_line.product_id.type not in ('product', 'consu'):
            return False
        move_name = _('PROD: %s') % production.name
        source_location_id = production.location_src_id.id

        if not destination_location_id:
            destination_location_id = source_location_id
        return stock_move.create(cr, uid, {
            'name': move_name,
            'picking_id': shipment_id,
            'product_id': production_line.product_id.id,
            'product_qty': production_line.product_qty,
            'product_uom': production_line.product_uom.id,
            'product_uos_qty': production_line.product_uos and
                                production_line.product_uos_qty or False,
            'product_uos': production_line.product_uos and
                            production_line.product_uos.id or False,
            'date': date_planned,
            'move_dest_id': parent_move_id,
            'location_id': source_location_id,
            'location_dest_id': destination_location_id,
            'state': 'waiting',
            'company_id': production.company_id.id,
        })

    def _make_production_internal_shipment2(self, cr, uid, production,
                                            context=None):
        ir_sequence = self.pool.get('ir.sequence')
        stock_picking = self.pool.get('stock.picking')
        routing_loc = None
        pick_type = 'internal'
        address_id = False

        # Take routing address as a Shipment Address.
        # If usage of routing location is a internal, make outgoing shipment
        # otherwise internal shipment
        if production.bom_id.routing_id and\
        production.bom_id.routing_id.location_id:
            routing_loc = production.bom_id.routing_id.location_id
            if routing_loc.usage != 'internal':
                pick_type = 'out'
            address_id = routing_loc.address_id and\
                        routing_loc.address_id.id or False

        # Take next Sequence number of shipment base on type
        pick_name = ir_sequence.get(cr, uid, 'stock.picking')
        picking_id = stock_picking.create(cr, uid, {
            'name': pick_name + '-' + context.get('type', ''),
            'origin': (production.origin or '').split(':')[0]\
                        + ':' + production.name,
            'type': pick_type,
            'state': 'draft',
            'address_id': address_id,
            'company_id': production.company_id.id,
        })
        return picking_id

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'picking_ids': []
        })
        return super(mrp_production, self).copy(cr, uid, id, default, context)


class stock_picking(osv.Model):
    _inherit = 'stock.picking'

    _columns = {
        'production_id': fields.many2one('mrp.production', 'Production')
    }
mrp_production()
