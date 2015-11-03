# coding: utf-8

from openerp import models, fields, api


class StockQuant(models.Model):
    _inherit = "stock.quant"

    material_cost = fields.Float(string='Material Cost')
    production_cost = fields.Float(string='Production Cost')
    subcontracting_cost = fields.Float(string='Subcontracting Cost')
    landed_cost = fields.Float(string='Landed Cost')

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
        if move.purchase_line_id:
            quant.write({'material_cost': quant.cost})
        return quant
