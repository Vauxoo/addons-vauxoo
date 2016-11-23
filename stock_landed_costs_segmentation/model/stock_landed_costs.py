# -*- coding: utf-8 -*-

from __future__ import division
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError

SEGMENTATION_COST = [
    ('landed_cost', 'Landed Cost'),
    ('subcontracting_cost', 'Subcontracting Cost'),
    ('material_cost', 'Material Cost'),
    ('production_cost', 'Production Cost'),
]


class StockLandedCostLines(models.Model):
    _inherit = 'stock.landed.cost.lines'

    segmentation_cost = fields.Selection(
        SEGMENTATION_COST,
        string='Segmentation',
    )


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    @api.model
    def _get_discrete_values(self, line_id, diff):
        res = super(StockLandedCost, self)._get_discrete_values(line_id, diff)
        res['segmentation_cost'] = line_id.cost_line_id.segmentation_cost
        return res

    @api.multi
    def button_validate(self):
        self.ensure_one()
        quant_obj = self.env['stock.quant']
        # ctx = dict(self._context)

        for cost in self:
            if cost.state != 'draft':
                raise UserError(
                    _('Only draft landed costs can be validated'))
            if not cost.valuation_adjustment_lines or \
                    not self._check_sum(cost):
                raise UserError(
                    _('You cannot validate a landed cost which has no valid '
                      'valuation adjustments lines. Did you click on '
                      'Compute?'))

            if not all([cl.segmentation_cost for cl in cost.cost_lines]):
                raise UserError(
                    _('Please fill the segmentation field in Cost Lines'))

            quant_dict = {}
            for line in cost.valuation_adjustment_lines:
                if not line.move_id or \
                        line.move_id.location_id.usage == 'internal':
                    continue

                create = False
                if line.move_id.location_id.usage not in (
                        'supplier', 'inventory', 'production'):
                    create = True

                segment = line.cost_line_id.segmentation_cost
                per_unit = line.final_cost / line.quantity
                diff = per_unit - line.former_cost_per_unit

                if create:
                    continue

                for quant in line.move_id.quant_ids:
                    if quant.id not in quant_dict:
                        quant_dict[quant.id] = {}
                        quant_dict[quant.id][segment] = getattr(
                            quant, segment) + diff
                    else:
                        if segment not in quant_dict[quant.id]:
                            quant_dict[quant.id][segment] = getattr(
                                quant, segment) + diff
                        else:
                            quant_dict[quant.id][segment] += diff

            for key, pair in quant_dict.items():
                quant_obj.sudo().browse(key).write(pair)

        return super(StockLandedCost, self).button_validate()
