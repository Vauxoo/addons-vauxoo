# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
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


class mrp_production(osv.Model):
    _inherit = 'mrp.production'

    def _product_produced(self, cr, uid, ids, field, args, context=None):
        stock_obj = self.pool.get('stock.move')
        res = {}
        for id in ids:
            total = 0.0
            prod_id = self.browse(cr, uid, id)
            loc_dest_prod = prod_id.location_dest_id and\
                prod_id.location_dest_id.id or ''
            product_prod = prod_id.product_id and\
                prod_id.product_id.id or ''
            if prod_id.move_created_ids2:
                for move in prod_id.move_created_ids2:
                    move_id = stock_obj.browse(cr, uid, move.id)
                    product_move = move_id.product_id and\
                        move_id.product_id.id or ''
                    loc_dest_move = move_id.location_dest_id and\
                        move_id.location_dest_id.id or ''
                    state_move = move_id.state or ''
                    if loc_dest_move == loc_dest_prod and\
                        state_move == 'done' and\
                            product_prod == product_move:
                        total_move = move_id.product_qty or 0.0
                        total = total + total_move
            res[id] = total
        return res

    def _product_in_stock(self, cr, uid, ids, field, args, context=None):
        stock_obj = self.pool.get('stock.move')
        res = {}
        for id in ids:
            total_des = 0.0
            total = 0.0
            prod_id = self.browse(cr, uid, id)
            loc_dest_prod = prod_id.location_dest_id and\
                prod_id.location_dest_id.id or ''
            product_prod = prod_id.product_id and prod_id.product_id.id or ''
            if prod_id.move_created_ids2:
                for move in prod_id.move_created_ids2:
                    move_id = stock_obj.browse(cr, uid, move.id)
                    loc_dest_move = move_id.location_dest_id and\
                        move_id.location_dest_id.id or ''
                    state_move = move_id.state or ''
                    product_move = move_id.product_id and\
                        move_id.product_id.id or ''
                    if loc_dest_move != loc_dest_prod and\
                        state_move == 'done' and\
                            product_prod == product_move:
                        total_move = move_id.product_qty or 0.0
                        total_des = total_des + total_move
                    total_produced = prod_id.product_produced or 0.0
                    total = total_produced - total_des
            res[id] = total
        return res

    _columns = {
        'product_produced': fields.function(_product_produced, method=True,
                                            type="float",
                                            string='Total Produced'),
        'product_in_stock': fields.function(_product_in_stock, method=True,
                                            type="float",
                                            string='Total In Stock'),
    }
