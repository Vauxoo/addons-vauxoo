from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_threshold = fields.Float(
        default=lambda self: self.env.user.company_id.margin_threshold, help="Limit margin set in sales configuration"
    )

    @api.depends("price_subtotal", "product_uom_qty", "purchase_price")
    def _compute_margin(self):
        res = super()._compute_margin()
        for line in self:
            if not line.product_uom_qty:
                line.margin_percent = 0.0
                continue

            currency = line.currency_id
            if currency.is_zero(line.price_unit) or currency.is_zero(line.price_subtotal):
                line.margin_percent = -1.0
                continue

            purchase_price = line.purchase_price or line.product_id.standard_price
            if currency.is_zero(purchase_price):
                line.margin_percent = 1.0
                continue

        return res
