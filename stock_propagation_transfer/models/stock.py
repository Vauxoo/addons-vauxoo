# -*- coding: utf-8 -*-

from openerp import api, models


class StockMove(models.Model):

    _inherit = "stock.move"

    @api.multi
    def action_done(self):
        """Inherit action_done to verify if it have to propagate transfer to
        move_dest_id.
        """
        res = super(StockMove, self).action_done()
        if self.move_dest_id and self.move_dest_id.rule_id.propagate_transfer:
            picking = self.move_dest_id.picking_id
            ctx = {
                'active_id': picking.id,
                'active_ids': [picking.id],
                'active_model': 'stock.picking',
            }
            wizard_transfer_id = self.env['stock.transfer_details'].\
                with_context(ctx).create({'picking_id': picking.id})
            wizard_transfer_id.do_detailed_transfer()
        return res
