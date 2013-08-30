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
        @return: The first Lot to produce (cardinal order).
        """
        context = context or {}
        production_obj = self.pool.get('mrp.production')
        if context.get('active_id', False):
            production_id = context.get('active_id')
            res = production_obj.browse(
                cr, uid, production_id, context=context).wo_lot_ids[0].id
        else:
            raise osv.except_osv(_('Error!'), _('No define active_id'))
        return res

    _columns = {
        'production_id': fields.many2one(
            'mrp.production',
            string=_('Manufacturing Order'),
            help=_('Manufacturing Order')),
        'wo_lot_id': fields.many2one(
            'mrp.workoder.lot',
            required=True,
            string=_('Scheduled Work Orders Lots'),
            help=_('Scheduled Work Orders Lots.')),
    }

    _defaults = {
        'production_id': lambda s, c, u, ctx: ctx.get('active_id', False),
        'wo_lot_id': _get_default_wo_lot,
    }

    def onchange_wo_lot_ids(self, cr, uid, ids, production_id, wo_lot_id,
                            consume_line_ids, context=None):
        """
        Loads product information from the scheduled work order selected.
        @param production_id: manufacturing order id.
        @param wo_lot_id: selected scheduled work order lot.
        @param consume_line_ids: current cosumne product lines.
        """

        context = context or {}
        values = []
        production = self.pool.get('mrp.production').browse(
            cr, uid, production_id, context=context)
        wo_lot_obj = self.pool.get('mrp.workoder.lot')

        if wo_lot_id:
            wo_lot = wo_lot_obj.browse(cr, uid, wo_lot_id, context=context)
            for product_line in production.product_lines:
                values += [
                    {'product_id': product_line.product_id.id,
                     'quantity': product_line.product_qty * wo_lot.percentage/100.0,
                     'product_uom': product_line.product_uom.id}]

        return {'value': {'consume_line_ids': values}}
