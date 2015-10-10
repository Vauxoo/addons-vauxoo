# -*- coding: utf-8 -*-

from openerp import models, api, _
from openerp.exceptions import Warning


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    @api.multi
    def button_validate(self):
        self.ensure_one()
        quant_obj = self.env['stock.quant']
        # ctx = dict(self._context)

        for cost in self:
            if cost.state != 'draft':
                raise Warning(
                    _('Only draft landed costs can be validated'))
            if not cost.valuation_adjustment_lines or \
                    not self._check_sum(cost):
                raise Warning(
                    _('You cannot validate a landed cost which has no valid '
                      'valuation adjustments lines. Did you click on '
                      'Compute?'))

            quant_dict = {}
            for line in cost.valuation_adjustment_lines:
                if not line.move_id:
                    continue

                per_unit = line.final_cost / line.quantity
                diff = per_unit - line.former_cost_per_unit

                for quant in line.move_id.quant_ids:
                    if quant.id not in quant_dict:
                        quant_dict[quant.id] = quant.landed_cost + diff
                    else:
                        quant_dict[quant.id] += diff
                for key, value in quant_dict.items():
                    quant_obj.browse(key).write(
                        {'landed_cost': value})
        return super(StockLandedCost, self).button_validate()
