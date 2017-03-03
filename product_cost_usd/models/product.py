# -*- coding: utf-8 -*-
# Copyright 2017 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import odoo.addons.decimal_precision as dp
from odoo.tools import float_compare

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains('standard_price_usd', 'seller_ids')
    def check_cost_and_price(self):
        """ Validate 'Cost in USD' usability.

        Usability conditions:
        - If product type is not a service, before set a 'Cost in USD' in a
          product at least one supplier should have price in USD.
        - The Cost in USD cannot be less than supplier price.
        """
        usd_currency = self.env.ref('base.USD')
        prec = self.env['decimal.precision'].precision_get('Product Price')
        usd_seller = self.seller_ids.filtered(
            lambda x: x.currency_id == usd_currency)
        list_price = usd_seller.price if usd_seller else 0.0
        standard_price_usd = self.standard_price_usd
        product_type = self.type
        if not 'service' in product_type and not usd_seller and float_compare(
                standard_price_usd, 0, precision_digits=prec) > 0:
            raise ValidationError(
                _('You must have at least one supplier with price in USD'
                  ' before assign a Cost in USD'))
        if float_compare(
                list_price, standard_price_usd, precision_digits=prec) > 0:
            raise ValidationError(
                _('You cannot create or modify a product if the cost in USD'
                  ' is less than the supplier list price.\n\n'
                  '- Supplier list price = %s\n'
                  '- Cost in USD = %s') % (list_price, standard_price_usd))

    standard_price_usd = fields.Float(
        'Cost in USD',
        digits=dp.get_precision('Product Price'),
        help="Price cost of the product in USD currency")
