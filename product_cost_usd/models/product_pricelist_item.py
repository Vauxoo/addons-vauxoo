from odoo import fields, models


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    base = fields.Selection(
        selection_add=[("standard_price_usd", "Cost in USD")], ondelete={"standard_price_usd": "set default"}
    )

    def _compute_base_price(self, product, quantity, uom, date, currency, **kwargs):
        """Compute the base price for a pricelist item based on the USD standard price.

        This method overrides the native base price computation to inject our custom
        'standard_price_usd' base. When this specific base is selected in the pricelist
        item, the method performs the following pipeline:
        1. Retrieves the raw USD cost from the product (`standard_price_usd`).
        2. Adjusts the price according to the requested Unit of Measure (UoM) to ensure
           correct pricing for different quantities (e.g., dozens vs. units).
        3. Converts the adjusted USD price into the pricelist's target currency.

        By returning the exact converted base price at this stage, we allow Odoo's
        native pricing engine to seamlessly handle subsequent operations like discounts,
        surcharges, and financial rounding rules.
        """
        if self.base != "standard_price_usd":
            return super()._compute_base_price(product, quantity, uom, date, currency, **kwargs)
        target_currency = currency or self.currency_id
        usd_currency = self.env.ref("base.USD", raise_if_not_found=False)

        # 1. Retrieve the raw USD cost from the product
        price = product.standard_price_usd

        # 2. Unit of Measure conversion
        if product.uom_id != uom:
            price = product.uom_id._compute_price(price, uom)

        # 3. Convert from USD to the target pricelist currency
        # We set round=False to allow Odoo's native engine to apply its own rounding rules at the end
        if usd_currency and target_currency != usd_currency:
            price = usd_currency._convert(price, target_currency, self.env.company, date, round=False)
        return price
