# coding: utf-8

from odoo import models, fields, api
SEGMENTATION_COST = [
    'landed_cost',
    'subcontracting_cost',
    'material_cost',
    'production_cost',
]

SEGMENTATION_SELECTION = [
    ('landed_cost', 'Landed Cost'),
    ('subcontracting_cost', 'Subcontracting Cost'),
    ('material_cost', 'Material Cost'),
    ('production_cost', 'Production Cost'),
]


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    segmentation_cost = fields.Selection(
        SEGMENTATION_SELECTION,
        string='Segmentation',
    )


class MrpProduction(models.Model):
    """Production Orders / Manufacturing Orders
    """
    _inherit = 'mrp.production'
    _description = 'Manufacturing Order'

    @api.multi
    def adjust_move_segmentation_cost(self):
        self.ensure_one()

        sgmnt_dict = {}.fromkeys(SEGMENTATION_COST, 0.0)
        for fn in SEGMENTATION_COST:
            sgmnt_dict[fn] = sum(
                [move2.quantity * move2.origin_move_id[fn]
                 for raw_mat2 in self.move_raw_ids
                 for move2 in raw_mat2.move_orig_logistic_ids])

        finished_moves = self.move_finished_ids.filtered(
            lambda a: a.state == 'done')

        qty = sum([move.product_uom_qty for move in finished_moves])

        for fg_move in finished_moves:
            values = {}.fromkeys(SEGMENTATION_COST, 0.0)
            for fn in SEGMENTATION_COST:
                values[fn] = fg_move[fn] + sgmnt_dict[fn] / qty
            fg_move.sudo().write(values)
        return True

    @api.multi
    def get_workcenter_segmentation_amount(self):
        self.ensure_one()
        res = {}.fromkeys(SEGMENTATION_COST, 0.0)
        for wc_line in self.workorder_ids:
            wc = wc_line.workcenter_id
            fn = wc.segmentation_cost or 'production_cost'
            if self.routing_id.journal_id and wc.costs_general_account_id:
                # Cost per hour
                res[fn] += (wc_line.duration / 60.0) * wc.costs_hour
                # Cost per cycle
                # TODO: I did not find a similar field
                # res[fn] += wc_line.cycle * wc.costs_cycle
        return res

    @api.multi
    def adjust_move_production_cost(self):
        self.ensure_one()
        # NOTE: Updating production_cost in segmentation applies to all
        # products AVG, REAL & STD
        finished_moves = self.move_finished_ids.filtered(
            lambda a: a.state == 'done')
        qty = sum([move.product_uom_qty for move in finished_moves])

        if not qty:
            return False

        sgmnt_dict = self.get_workcenter_segmentation_amount()
        for qnt in finished_moves:
            values = {}.fromkeys(SEGMENTATION_COST, 0.0)
            for fn in SEGMENTATION_COST:
                values[fn] = qnt[fn] + sgmnt_dict[fn] / qty
            qnt.sudo().write(values)
        return True

    def _costs_generate(self):
        res = super(MrpProduction, self)._costs_generate()
        # NOTE: Add segmentation cost to quants in finished goods
        self.adjust_move_production_cost()
        # NOTE: increase/decrease segmentation cost on quants from raw
        # material
        self.adjust_move_segmentation_cost()
        return res
