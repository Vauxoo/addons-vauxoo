from collections import defaultdict

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.tools import float_round


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

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
        digits=dp.get_precision('Product Unit of Measure'),
        help='Quantity available to produce considering the quantities '
        'reserved by the order')

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
        for res in self.move_raw_ids.filtered(lambda move: not move.is_done):
            result[res.product_id.id] += (res.reserved_availability -
                                          res.quantity_done)

        for line, line_data in lines:
            if line.product_id.type in ('service', 'consu'):
                continue
            lines_dict[line.product_id.id] += line_data['qty'] / quantity
        qty = [(result[key] / val) for key, val in lines_dict.items() if val]
        return (float_round(
            min(qty) * self.bom_id.product_qty, 0, rounding_method='DOWN') if
            qty and min(qty) >= 0.0 else 0.0)

    def _workorders_create(self, bom, bom_data):
        workorders = super()._workorders_create(bom, bom_data)
        ready_wk = workorders.filtered(lambda wk: wk.state == 'ready')
        moves = self.move_raw_ids.filtered(lambda mv: mv.workorder_id)
        moves.write({'workorder_id': ready_wk.id})
        return workorders


class MrpWorkorder(models.Model):

    _inherit = 'mrp.workorder'

    def record_production(self):
        res = super(MrpWorkorder, self).record_production()
        for move in self.move_raw_ids.filtered(
                lambda mov: mov.state not in ('done', 'cancel')
                and mov.quantity_done > 0):
            context = self._context.copy()
            context['mrp_record_production'] = True
            move.with_context(context)._action_done()
        if not self.next_work_order_id:
            finished_moves = self.production_id.move_finished_ids
            production_moves = finished_moves.filtered(
                lambda x: (x.product_id.id == self.production_id.product_id.id)
                and (x.state not in ('done', 'cancel'))
                and x.quantity_done > 0)
            for production_move in production_moves:
                production_move._action_done()
        return res
