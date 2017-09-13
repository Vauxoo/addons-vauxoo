# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from collections import defaultdict
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
    def get_qty_available_to_produce(self):
        """Compute the total available to produce considering
        the lines reserved
        """
        self.ensure_one()

        quantity = self.product_uom_id._compute_quantity(
            self.product_qty, self.bom_id.product_uom_id)
        if not quantity:
            return 0

        lines = self.bom_id.explode(self.product_id, quantity)[1]

        result, lines_dict = defaultdict(int), defaultdict(int)
        for res in self.move_raw_ids:
            result[res.product_id.id] += res.reserved_availability

        for line, line_data in lines:
            lines_dict[line.product_id.id] += line_data['qty'] / quantity

        qty = [(int(result[key] / val)) for key, val in lines_dict.items()
               if val]

        return min(qty) if qty else 0.0
