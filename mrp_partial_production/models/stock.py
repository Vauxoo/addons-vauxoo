# coding: utf-8

from odoo import models


class StockMove(models.Model):

    _inherit = 'stock.move'

    def _split(self, qty, restrict_partner_id=False):
        if not self._context.get('mrp_record_production'):
            return super(StockMove, self)._split(qty, restrict_partner_id)

        amls = self.move_line_ids.filtered(
            lambda aml: aml.qty_done > 0 and
            aml.product_uom_qty > aml.qty_done)
        new_move_id = super(StockMove, self)._split(qty, restrict_partner_id)
        new_move = self.browse(new_move_id)
        for aml in amls:
            product_uom_qty = aml.product_uom_qty - aml.qty_done
            new_move.with_context(workorder_id=aml.workorder_id.id)._update_reserved_quantity(
                new_move.product_uom_qty, product_uom_qty, aml.location_id,
                aml.lot_id, aml.package_id, aml.owner_id)
        new_move._recompute_state()
        return new_move_id

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        res = super(StockMove, self)._prepare_move_line_vals(quantity, reserved_quant)
        if self._context.get('mrp_record_production'):
            res.update({
                'workorder_id': self._context.get('workorder_id') or False,
            })
        return res
