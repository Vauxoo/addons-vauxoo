from odoo import fields, models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        """Inherited to modify price computation when a pricelist item is
        based on cost in USD.

        Why this inheritance?

        This method always computes the product price, from product currency
        (mostly the same company currency) into pricelist currency. When the
        pricelist item is based on cost in USD is necessary that currency
        conversion is made from USD currency. For this reason, we must go back
        the conversion made in super and then made a conversion from USD
        currency to the pricelist currency to get the expected price when the
        pricelist item is based on cost in USD.

        Returns: dict{product_id: (price, suitable_rule) for given pricelist}

        If date in context: Date of the pricelist (%Y-%m-%d)

        :param products_qty_partner: list of typles products, quantity, partner
        :param datetime date: validity date
        :param ID uom_id: intermediate unit of measure
        """
        results = super()._compute_price_rule(products_qty_partner, date=date, uom_id=uom_id)
        usd_currency = self.env.ref("base.USD")
        date = fields.Date.context_today(self)
        for product_qty_partner in products_qty_partner:
            product = product_qty_partner[0]
            # get current price and pricelist item for product_id
            price, item_id = results[product.id]
            suitable_rule = self.item_ids.filtered(lambda x: x.id == item_id)
            # look that pricelist item is based on cost in usd
            if not suitable_rule or suitable_rule.base != "standard_price_usd":
                continue
            # go back conversion made in super, moving the price into
            # product currency for items based on cost in USD
            price = self.currency_id._convert(price, product.currency_id, self.env.company, date, round=False)
            # now convert from USD into pricelist currency
            if self.currency_id != usd_currency:
                price = usd_currency._convert(price, self.currency_id, self.env.company, date, round=False)
            results[product.id] = (price, suitable_rule and suitable_rule.id or False)
        return results
