# coding: utf-8

from odoo import models


class StockMove(models.Model):

    _inherit = 'stock.move'

    def _split(self, qty, restrict_partner_id=False):
        if not self._context.get('mrp_record_production'):
            return super(StockMove, self)._split(qty, restrict_partner_id)

        amls = self.move_line_ids.filtered(
            lambda aml: aml.qty_done > 0 and aml.product_uom_qty > aml.qty_done)
        aml_vals = []
        for aml in amls:
            vals = {
                'product_id': aml.product_id.id,
                'product_uom_qty': aml.product_uom_qty - aml.qty_done,
                'product_uom_id': aml.product_uom_id.id,
                'workorder_id': aml.workorder_id.id,
                'location_id': aml.location_id.id,
                'location_dest_id': aml.location_dest_id.id,
                'picking_id': aml.picking_id.id,
                'lot_id': aml.lot_id.id or False,
                'package_id': aml.package_id.id or False,
                'owner_id': aml.owner_id.id or False,
            }
            aml_vals.append(vals)
        new_move_id = super(StockMove, self)._split(qty, restrict_partner_id)
        for vals in aml_vals:
            vals['move_id'] = new_move_id
            new_aml = self.env['stock.move.line'].create(vals)
        self.browse(new_move_id)._recompute_state()
        return new_move_id
