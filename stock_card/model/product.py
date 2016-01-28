# -*- coding: utf-8 -*-

from openerp import models, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def stock_card_move_get(self):
        self.ensure_one()
        scp_obj = self.env['stock.card.product']
        scp_brw = scp_obj.create({'product_id': self._ids})
        return scp_brw.stock_card_move_get()
