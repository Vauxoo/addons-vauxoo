from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class ProductTemplate(models.Model):
    _inherit = "product.template"

    currency_usd_id = fields.Many2one(
        "res.currency",
        string="Currency USD",
        compute="_compute_currency_usd_id",
        help="Technical field to show the price fields as USD in the products",
    )
    standard_price_usd = fields.Float(
        "Cost in USD",
        digits="Product Price",
        help="Price cost of the product in USD currency",
    )

    def _compute_currency_usd_id(self):
        currency_usd = self.env.ref("base.USD")
        for product in self:
            product.currency_usd_id = currency_usd

    @api.constrains("standard_price_usd", "seller_ids")
    def check_cost_and_price(self):
        """Validate 'Cost in USD' usability.

        Usability conditions:
        - Before set a 'Cost in USD' in a product at least one supplier should
          have price in USD.
        - The Cost in USD cannot be less than supplier price.
        """
        usd_currency = self.env.ref("base.USD")
        prec = self.env["decimal.precision"].precision_get("Product Price")
        for product in self:
            usd_seller = product.seller_ids.filtered(lambda x: x.currency_id == usd_currency)[:1]
            list_price = usd_seller.price
            standard_price_usd = product.standard_price_usd
            if not usd_seller and float_compare(standard_price_usd, 0, precision_digits=prec) > 0:
                raise ValidationError(
                    _("You must have at least one supplier with price in USD before assigning a Cost in USD")
                )
            if float_compare(list_price, standard_price_usd, precision_digits=prec) > 0:
                raise ValidationError(
                    _(
                        "You cannot create or modify a product if the cost in USD"
                        " is less than the supplier list price.\n\n"
                        "- Supplier list price = %s\n"
                        "- Cost in USD = %s",
                        list_price,
                        standard_price_usd,
                    )
                )
