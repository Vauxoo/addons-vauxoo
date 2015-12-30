# coding: utf-8

from openerp import models, fields, api
from openerp import SUPERUSER_ID

SEGMENTATION_COST = [
    'landed_cost',
    'subcontracting_cost',
    'material_cost',
    'production_cost',
]


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.depends('material_cost', 'production_cost', 'landed_cost',
                 'subcontracting_cost')
    def _compute_segmentation(self):
        for record in self:
            record.segmentation_cost = sum([
                getattr(record, fn) for fn in SEGMENTATION_COST])

    material_cost = fields.Float(string='Material Cost')
    production_cost = fields.Float(string='Production Cost')
    subcontracting_cost = fields.Float(string='Subcontracting Cost')
    landed_cost = fields.Float(string='Landed Cost')
    segmentation_cost = fields.Float(
        string='Actual Cost', store=True, readonly=True,
        compute='_compute_segmentation',
        help=("Provides the actual cost for this transaction. "
              "It is computed from the sum of the segmentation costs: "
              "`material cost`, `subcontracting cost`, `landed cost` "
              "& `production cost`"))

    @api.v7
    def _quant_create(
            self, cr, uid, qty, move, lot_id=False, owner_id=False,
            src_package_id=False, dest_package_id=False,
            force_location_from=False, force_location_to=False, context=None):
        quant = super(StockQuant, self)._quant_create(
            cr, uid, qty, move, lot_id=lot_id, owner_id=owner_id,
            src_package_id=src_package_id, dest_package_id=dest_package_id,
            force_location_from=force_location_from,
            force_location_to=force_location_to, context=context)
        if move.purchase_line_id or move.inventory_id:
            self.write(
                cr, SUPERUSER_ID, quant.id, {'material_cost': quant.cost},
                context=context)
        return quant
