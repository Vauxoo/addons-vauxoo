# coding: utf-8

from __future__ import division
from openerp import models, fields, api
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
    def adjust_quant_segmentation_cost(self):
        self.ensure_one()
        quant_obj = self.env['stock.quant']

        sgmnt_dict = {}.fromkeys(SEGMENTATION_COST, 0.0)
        for fn in SEGMENTATION_COST:
            sgmnt_dict[fn] = sum([
                quant2.qty * getattr(quant2, fn)
                for raw_mat2 in self.move_lines2
                for quant2 in raw_mat2.quant_ids])

        fg_quants = [quant for raw_mat in self.move_created_ids2
                     for quant in raw_mat.quant_ids]

        qty = sum([quant.qty for quant in fg_quants])

        for fg_quant in fg_quants:
            values = {}.fromkeys(SEGMENTATION_COST, 0.0)
            for fn in SEGMENTATION_COST:
                values[fn] = getattr(fg_quant, fn) + sgmnt_dict[fn] / qty
            quant_obj.sudo().browse(fg_quant.id).write(values)
        return True

    @api.multi
    def get_workcenter_segmentation_amount(self):
        self.ensure_one()
        res = {}.fromkeys(SEGMENTATION_COST, 0.0)
        for wc_line in self.workcenter_lines:
            wc = wc_line.workcenter_id
            fn = wc.segmentation_cost or 'production_cost'
            if wc.costs_journal_id and wc.costs_general_account_id:
                # Cost per hour
                res[fn] += wc_line.hour * wc.costs_hour
                # Cost per cycle
                res[fn] += wc_line.cycle * wc.costs_cycle
        return res

    @api.multi
    def adjust_quant_production_cost(self, amount):
        self.ensure_one()
        quant_obj = self.env['stock.quant']
        # NOTE: Updating production_cost in segmentation applies to all
        # products AVG, REAL & STD
        all_quants = [quant for raw_mat in self.move_created_ids2
                      for quant in raw_mat.quant_ids]
        qty = sum([quant.qty for quant in all_quants])

        if not qty:
            return False

        sgmnt_dict = self.get_workcenter_segmentation_amount()
        for qnt in all_quants:
            values = {}.fromkeys(SEGMENTATION_COST, 0.0)
            for fn in SEGMENTATION_COST:
                values[fn] = getattr(qnt, fn) + sgmnt_dict[fn] / qty
            quant_obj.sudo().browse(qnt.id).write(values)
        return True

    @api.v7
    def refresh_quant(self, cr, uid, production, amount, diff):
        """Method that allow to refresh values for quant & segmentation costs
        """

        super(MrpProduction, self).refresh_quant(
            cr, uid, production, amount, diff)

        # NOTE: Add segmentation cost to quants in finished goods
        self.adjust_quant_production_cost(cr, uid, production.id, amount)
        # NOTE: increase/decrease segmentation cost on quants from raw
        # material
        self.adjust_quant_segmentation_cost(cr, uid, production.id)

        return amount
