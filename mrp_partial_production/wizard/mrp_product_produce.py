# -*- coding: utf-8 -*-
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, _
from odoo.exceptions import Warning as UserError


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    @api.model
    def default_get(self, fields):
        res = super(MrpProductProduce, self).default_get(fields)
        if self._context.get('active_id'):
            production = self.env['mrp.production'].browse(
                self._context['active_id'])
            res['product_qty'] = (res['product_qty'] > 0 and
                                  production.qty_available_to_produce)
        return res

    @api.multi
    def do_produce(self):
        self.ensure_one()
        if self.product_qty > self.production_id.qty_available_to_produce:
            raise UserError(_('''You cannot produce more than available to
                                produce for this order'''))
        return super(MrpProductProduce, self).do_produce()
