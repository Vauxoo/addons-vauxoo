# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.odoo.com>
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

from openerp import models, fields, api


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    quick_view = fields.Boolean(
        related='picking_id.picking_type_id.quick_view', readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(StockTransferDetails, self).default_get(fields)
        picking_ids = self._context.get('active_ids')
        picking_id, = picking_ids
        picking = self.env['stock.picking'].browse(picking_id)
        if picking.picking_type_id.quick_view and res.get('item_ids', []):
            new_items = []
            for item in res.get('item_ids'):
                sourceloc_id = picking.force_location_id.id
                destinationloc_id = picking.force_location_dest_id.id
                item.update({'sourceloc_id': sourceloc_id,
                             'destinationloc_id': destinationloc_id})
                new_items.append(item)
            res['item_ids'] = new_items
        return res
