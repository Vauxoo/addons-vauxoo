# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Jose Suniaga <josemiguel@vauxoo.com>
#    Planned by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Audited by: Jose Morales <jose@vauxoo.com>
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
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def _check_quants_availability(self):
        for record in self:
            domain_quants = [
                ('product_id', '=', record.product_id.id),
                ('location_id', 'child_of', record.location_id.id),
                ('reservation_id', '=', False)
            ]
            quants = self.env['stock.quant'].read_group(
                domain_quants, ['product_id', 'location_id', 'qty'],
                ['location_id', 'product_id'], orderby='qty ASC')
            total_qty = quants and quants[0].get('qty') or 0.0
            if total_qty == 0.0:
                raise UserError(
                    _("Product %s not have availability in %s. \n\n"
                      "Please check your inventory, receipts or deliveries"
                      % (record.product_id.name, record.location_id.name)))
            elif record.product_uom_qty > total_qty:
                raise UserError(
                    _("Product %s only has %s %s available in %s."
                      % (record.product_id.name, total_qty,
                         record.product_uom.name, record.location_id.name)))
        return True

    @api.multi
    def location_id_change(self, location_id):
        quant = self.env['stock.quant'].search([
            ('location_id', 'child_of', location_id),
            ('qty', '>=', 1.0),
            ('reservation_id', '=', False)])

        product = quant.mapped("product_id")
        return {'domain': {'product_id': [('id', 'in', product.ids)]}}

    @api.multi
    def unlink(self):
        context = self._context
        if context.get('active_model') == 'stock.picking.type' and \
                context.get('active_id'):
            picking_id = context.get('active_id')
            picking_type = self.env['stock.picking.type'].browse(picking_id)
            if picking_type.quick_view:
                for move in self:
                    if move.state == 'confirmed':
                        move.action_cancel()
                        # move.unlink()
        return super(StockMove, self).unlink()


class StockPicking(models.Model):
    _inherit = "stock.picking"

    force_location_id = fields.Many2one(
        'stock.location', string="Source Location", readonly=True,
        states={'draft': [('readonly', False)]})
    force_location_dest_id = fields.Many2one(
        'stock.location', string="Destination Location", readonly=False,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    @api.model
    def _prepare_pack_ops(self, picking, quants, force_qties):
        res = super(StockPicking, self)._prepare_pack_ops(
            picking, quants, force_qties)
        for item in res:
            if 'picking_id' in item:
                picking = self.env['stock.picking'].browse(item['picking_id'])
                if picking.picking_type_id.quick_view:
                    item.update({
                        'location_id': picking.force_location_id.id,
                        'location_dest_id': picking.force_location_dest_id.id})
        return res

    @api.onchange('force_location_id', 'force_location_dest_id')
    def onchange_force_locations(self):
        for pick in self:
            move_vals = {}
            if pick.force_location_id and \
                    not pick.force_location_dest_id:
                move_vals = {
                    'location_id': pick.force_location_id.id}
            elif not pick.force_location_id and \
                    pick.force_location_dest_id:
                move_vals = {
                    'location_dest_id': pick.force_location_dest_id.id}
            elif pick.force_location_id and \
                    pick.force_location_dest_id:
                move_vals = {
                    'location_id': pick.force_location_id.id,
                    'location_dest_id': pick.force_location_dest_id.id}
            if move_vals:
                for move in pick.move_lines:
                    move.update(move_vals)

    @api.multi
    def action_assign(self):
        for pick in self:
            if pick.picking_type_id.quick_view and \
                    not pick.force_location_id:
                raise UserError(
                    _("You should set source location before check"
                      " availability"))
            elif pick.picking_type_id.quick_view:
                moves = pick.move_lines.filtered(
                    lambda m: m.state not in ('draft', 'cancel', 'done'))
                moves._check_quants_availability()
                if pick.force_location_dest_id:
                    location_dest_id = pick.force_location_dest_id.id
                    for move in moves:
                        move.write({'location_dest_id': location_dest_id})
        return super(StockPicking, self).action_assign()


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    quick_view = fields.Boolean('Use Quick View')


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    easy_internal_type_id = fields.Many2one(
        'stock.picking.type', string="Quick Internal Type"
    )
    use_easy_internal = fields.Boolean(
        string="Quick Internal transfers in this warehouse", default=False
    )

    @api.model
    def create_sequence(self, warehouse_id, name, prefix, padding):
        return self.env['ir.sequence'].sudo().\
            create(values={
                'name': warehouse_id.name + name,
                'prefix': warehouse_id.code + prefix,
                'padding': padding,
                'company_id': warehouse_id.company_id.id
            })

    @api.model
    def compute_next_color(self):
        """
        Choose the next available color for
        the picking types of this warehouse
        """
        available_colors = [c % 9 for c in range(3, 12)]
        all_used_colors = self.env['stock.picking.type'].search_read([
            ('warehouse_id', '!=', False),
            ('color', '!=', False)
            ], ['color'], order='color')
        for col in all_used_colors:
            if col['color'] in available_colors:
                available_colors.remove(col['color'])
        return available_colors[0] if available_colors else 0

    @api.multi
    def create_easy_internal(self, use_easy_internal=False):
        picking_type = self.env['stock.picking.type']
        warehouse = self
        if not use_easy_internal:
            use_easy_internal = warehouse.use_easy_internal
        easy_internal_type_id = warehouse.easy_internal_type_id and \
            warehouse.easy_internal_type_id.id or False

        # create new sequence
        if use_easy_internal and not easy_internal_type_id:
            seq_name = _(' Sequence Quick internal transfers')
            easy_internal_seq_id = self.create_sequence(
                warehouse, seq_name, '/QUICK/INT/', 5)

        color = self.compute_next_color()

        # order the picking types with a sequence
        # allowing to have the following suit for
        # each warehouse: reception, internal, pick, pack, ship.
        max_sequence = self.env['stock.picking.type'].search_read(
            [], ['sequence'], order='sequence desc')
        max_sequence = max_sequence and max_sequence[0]['sequence'] or 0
        if use_easy_internal and not easy_internal_type_id:
            easy_internal_ptype = picking_type.create({
                'name': _('Quick Internal Transfers'),
                'warehouse_id': warehouse.id,
                'code': 'internal',
                'quick_view': True,
                'sequence_id': easy_internal_seq_id.id,
                'default_location_src_id': warehouse.lot_stock_id.id,
                'default_location_dest_id': warehouse.lot_stock_id.id,
                'sequence': max_sequence + 1,
                'color': color
            })
            easy_internal_type_id = easy_internal_ptype.id
        return easy_internal_type_id

    @api.model
    def create_sequences_and_picking_types(self, warehouse):
        res = super(StockWarehouse, self).create_sequences_and_picking_types(
            warehouse)
        easy_internal_type_id = warehouse.create_easy_internal()
        if easy_internal_type_id:
            warehouse.write({'easy_internal_type_id': easy_internal_type_id})
        return res

    @api.multi
    def write(self, vals):
        for record in self:
            if 'use_easy_internal' in vals and vals['use_easy_internal']:
                if record.easy_internal_type_id:
                    record.easy_internal_type_id.write({'active': True})
                easy_internal_type_id = record.create_easy_internal(
                    use_easy_internal=True)
                vals.update({'easy_internal_type_id': easy_internal_type_id})
            elif 'use_easy_internal' in vals and not vals['use_easy_internal']:
                if record.easy_internal_type_id:
                    record.easy_internal_type_id.write({'active': False})
        return super(StockWarehouse, self).write(vals=vals)
