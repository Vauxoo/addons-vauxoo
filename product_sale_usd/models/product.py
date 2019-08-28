# -*- coding: utf-8 -*-
# Copyright 2019 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons import decimal_precision as dp
from odoo import models, fields, api, _


class ProductTemplate(models.Model):

    _inherit = "product.template"

    @api.depends('sale_price_usd')
    def _compute_sale_price(self):
        usd_currency = self.env.ref('base.USD')
        company = self.env.user.company_id
        local_currency = company.currency_id
        for product in self:
            local_currency_value = local_currency._convert(
                product.sale_price_usd, usd_currency, company,
                fields.Date.today())
            product.list_price = local_currency_value

    def _inverse_sale_price(self):
        usd_currency = self.env.ref('base.USD')
        company = self.env.user.company_id
        currency = company.currency_id
        for product in self:
            usd_currency_value = usd_currency._convert(
                product.list_price, currency, company,
                fields.Date.today())
            product.sale_price_usd = usd_currency_value

    list_price = fields.Float(
        compute="_compute_sale_price",
        inverse="_inverse_sale_price",
    )

    sale_price_usd = fields.Float(
        'Sale Price in USD',
        digits=dp.get_precision('Product Price'),
        help="Sale price of the product in USD currency")
