# -*- coding: utf-8 -*-
# Copyright 2017 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import odoo.addons.decimal_precision as dp
from odoo.tools import float_compare

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends('seller_ids.price', 'seller_ids.currency_id')
    def _compute_standard_price_usd(self):
        usd_currency = self.env.ref('base.USD')
        usd_seller = self.seller_ids.filtered(
            lambda x: x.currency_id == usd_currency)
        self.standard_price_usd = usd_seller[0].price if usd_seller else 0.0

    standard_price_usd = fields.Float(
        'Cost in USD',
        compute='_compute_standard_price_usd',
        readonly=True,
        store=True,
        digits=dp.get_precision('Product Price'),
        help="Price cost of the product expressed in USD currency. To modify"
        " this cost you must go to the Purchasing tab, suppliers section and"
        " add/create a line with the cost of the product.")
