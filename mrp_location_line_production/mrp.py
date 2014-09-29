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
from openerp.osv import osv


class mrp_production(osv.Model):
    _inherit = 'mrp.production'

    def _make_production_produce_line(self, cr, uid, production, context=None):
        res = super(mrp_production, self)._make_production_produce_line(
            cr, uid, production, context=context)
        stock_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        product = stock_obj.browse(cr, uid, res).product_id.id
        location_prod = product_obj.browse(
            cr, uid, product).property_stock_production.id or False
        if location_prod:
            stock_obj.write(cr, uid, res, {'location_id': location_prod})
        return res

    def _make_production_consume_line(self, cr, uid, production_line,
                    parent_move_id, source_location_id=False, context=None):
        res = super(mrp_production, self)._make_production_consume_line(cr,
                    uid, production_line, parent_move_id,
                    source_location_id=source_location_id, context=context)
        stock_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        product = stock_obj.browse(cr, uid, res).product_id.id
        location_dest_prod = product_obj.browse(
            cr, uid, product).property_stock_production.id or False
        if location_dest_prod:
            stock_obj.write(cr, uid, res, {
                            'location_dest_id': location_dest_prod})
        return res
