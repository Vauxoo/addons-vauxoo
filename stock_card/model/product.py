# -*- coding: utf-8 -*-

import logging
from openerp import models, api, fields
_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    date_stock_card_border = fields.Datetime(string='Stock Card Border Date')

    @api.multi
    def stock_card_move_get(self):
        self.ensure_one()
        scp_obj = self.env['stock.card.product']
        scp_brw = scp_obj.create({'product_id': self._ids})
        return scp_brw.stock_card_move_get()

    @api.multi
    def stock_card_inquiry_get(self):
        self.ensure_one()
        obj = self.env['stock.card']
        brw = obj.create({'product_ids': [(4, self._ids)]})
        return brw.stock_card_inquiry_get()
