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
        self.ensure_one()
        result, lines_dict = {}, {}
        for res in self.move_raw_ids:
            if res.product_id.id not in result:
                result[res.product_id.id] = 0
            result[res.product_id.id] += res.reserved_availability

        quantity = self.product_uom_id._compute_quantity(
            self.product_qty, self.bom_id.product_uom_id)
        lines = self.bom_id.explode(self.product_id, quantity)[1]

        for line, line_data in lines:
            if line.product_id.id not in lines_dict:
                lines_dict[line.product_id.id] = 0
            lines_dict[line.product_id.id] += line_data['qty'] / quantity

        qty = [(int(result[key] / val)) for key, val in lines_dict.items()
               if val]

        return min(qty) if qty else 0.0
