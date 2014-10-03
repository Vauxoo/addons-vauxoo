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


from openerp.osv import osv, fields


class mrp_production(osv.Model):
    _inherit = "mrp.production"

    def _make_production_line_procurement(self, cr, uid, production_line,
                                          shipment_move_id, context=None):
        procurement_id = super(mrp_production,
            self)._make_production_line_procurement(
            cr, uid, production_line, shipment_move_id, context=context)
        procurement_order_pool = self.pool.get('procurement.order')
        procurement_order_pool.write(cr, uid, procurement_id, {
            'production_ids': [(4, production_line.production_id.id)]})
        return procurement_id

    _columns = {
        'procurement_ids': fields.many2many('procurement.order',
            'mrp_production_procurement_order_rel', 'production_id',
            'procurement_id', 'Production orders'),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'procurement_ids': [],
        })
        return super(mrp_production, self).copy(cr, uid, id, default, context)
