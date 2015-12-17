# coding: utf-8

from openerp import models, api
SEGMENTATION_COST = [
    'landed_cost',
    'subcontracting_cost',
    'material_cost',
    'production_cost',
]


class MrpProduction(models.Model):
    """
    Production Orders / Manufacturing Orders
    """
    _inherit = 'mrp.production'
    _description = 'Manufacturing Order'

    @api.multi
    def adjust_quant_segmentation_cost(self):
        self.ensure_one()

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
            fg_quant.write(values)
        return True

    @api.multi
    def adjust_quant_production_cost(self, amount):
        self.ensure_one()
        # NOTE: Updating production_cost in segmentation applies to all
        # products AVG, REAL & STD
        all_quants = [quant for raw_mat in self.move_created_ids2
                      for quant in raw_mat.quant_ids]
        qty = sum([quant.qty for quant in all_quants])

        for quant in all_quants:
            quant.write(
                {'production_cost': quant.production_cost + amount / qty})
        return True

    @api.v7
    def refresh_quant(self, cr, uid, production, amount, diff):
        """
        Method that allow to refresh values for quant & segmentation costs
        """

        super(MrpProduction, self).refresh_quant(
            cr, uid, production, amount, diff)

        if diff:
            # NOTE: Add segmentation cost to quants in finished goods
            self.adjust_quant_production_cost(cr, uid, production.id, amount)
            # NOTE: increase/decrease segmentation cost on quants from raw
            # material
            self.adjust_quant_segmentation_cost(cr, uid, production.id)

        return amount
