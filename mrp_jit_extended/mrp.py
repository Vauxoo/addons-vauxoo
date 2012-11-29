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
    
    def _make_production_line_procurement(self, cr, uid, production_line, shipment_move_id, context=None):
        procurement_order = self.pool.get('procurement.order')
        production = production_line.production_id
        location_id = production.location_src_id.id
        date_planned = production.date_planned
        procurement_name = (production.origin or '').split(':')[0] + ':' + production.name
        procurement_id = procurement_order.create(cr, uid, {
                    'name': procurement_name,
                    'origin': procurement_name,
                    'date_planned': date_planned,
                    'product_id': production_line.product_id.id,
                    'product_qty': production_line.product_qty,
                    'product_uom': production_line.product_uom.id,
                    'product_uos_qty': production_line.product_uos and production_line.product_qty or False,
                    'product_uos': production_line.product_uos and production_line.product_uos.id or False,
                    'location_id': location_id,
                    'procure_method': production_line.product_id.procure_method,
                    'move_id': shipment_move_id,
                    'company_id': production.company_id.id,
                    'production_id': production_line.production_id.id
                })
        #procurement_id = super(mrp_production, self)._make_production_line_procurement(cr, uid, production_line, shipment_move_id, context=context)
        return procurement_id

mrp_production()