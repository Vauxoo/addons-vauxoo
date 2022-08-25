from odoo import fields, models


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    base = fields.Selection(
        selection_add=[("standard_price_usd", "Cost in USD")], ondelete={"standard_price_usd": "set default"}
    )
