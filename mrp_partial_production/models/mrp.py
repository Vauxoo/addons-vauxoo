# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    @api.multi
    @api.depends('state', 'move_raw_ids')
    def _compute_qty_to_produce(self):
        """Used to shown the quantity available to produce considering the
        reserves in the moves related
        """
        for record in self:
            total = record.get_qty_available_to_produce()
            record.qty_available_to_produce = total

    qty_available_to_produce = fields.Float(
        compute='_compute_qty_to_produce', readonly=True,
        help='Quantity available to produce considering the quantities '
        'reserved by the order')

    @api.multi
    def test_ready(self):
        res = super(MrpProduction, self).test_ready()
        for record in self:
            if record.qty_available_to_produce > 0:
                res = True
        return res

    @api.multi
    def get_qty_available_to_produce(self):
        """Compute the total available to produce considering
        the lines reserved
        """
        qty = []
        for record in self:
            quantity = record.product_uom_id._compute_quantity(
                record.product_qty, record.bom_id.product_uom_id)
            boms, lines = record.bom_id.explode(record.product_id, quantity)

            for line, line_data in lines:
                move_line = record.move_raw_ids.filtered(
                    lambda li: li.bom_line_id.id == line.id)
                original_qty = line_data['qty'] / quantity
                qty.append(int(move_line.reserved_availability / original_qty)
                           if original_qty else 0)

        return min(qty) if qty else 0.0
