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
from tools.translate import _

class mrp_production(osv.osv):
    _inherit='mrp.production'
    
    _columns = {
        'picking_ids' : fields.one2many('stock.picking', 'production_id', 'Picking')
    }

    def _make_production_internal_shipment2(self, cr, uid, production, context=None):
        ir_sequence = self.pool.get('ir.sequence')
        stock_picking = self.pool.get('stock.picking')
        routing_loc = None
        pick_type = 'internal'
        address_id = False
        
        # Take routing address as a Shipment Address.
        # If usage of routing location is a internal, make outgoing shipment otherwise internal shipment
        if production.bom_id.routing_id and production.bom_id.routing_id.location_id:
            routing_loc = production.bom_id.routing_id.location_id
            if routing_loc.usage <> 'internal':
                pick_type = 'out'
            address_id = routing_loc.address_id and routing_loc.address_id.id or False

        # Take next Sequence number of shipment base on type
        pick_name = ir_sequence.get(cr, uid, 'stock.picking.' + pick_type)

        picking_id = stock_picking.create(cr, uid, {
            'name': pick_name+'-'+context.get('type',False),
            'origin': (production.origin or '').split(':')[0] + ':' + production.name,
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
mrp_production()

class stock_picking(osv.osv):
    _inherit='stock.picking'
    
    _columns = {
        'production_id' : fields.many2one('mrp.production', 'Production')
    }
stock_picking()
