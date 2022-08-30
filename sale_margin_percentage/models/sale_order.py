from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    margin_percentage = fields.Float(
        compute="_compute_margin_percentage",
        digits="Product Price",
        store=True,
        help="Margin percentage compute based on price unit",
    )

    @api.depends("order_line.margin_percentage")
    def _compute_margin_percentage(self):
        for order in self:
            lines = order.order_line.filtered(lambda r: r.state != "cancel")
            margin_sum = sum(lines.mapped("margin"))
            subtotal = order.amount_untaxed
            if not subtotal or not margin_sum:
                order.margin_percentage = 0.0
                continue
            order.margin_percentage = margin_sum * (100.0 / subtotal)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_threshold = fields.Float(
        default=lambda self: self.env.user.company_id.margin_threshold, help="Limit margin set in sales configuration"
    )
    margin_percentage = fields.Float(
        compute="_compute_margin_percentage",
        digits="Product Price",
        store=True,
        help="Margin percentage compute based on price unit",
    )
    purchase_price = fields.Float(readonly=True, help="Price purchase of product")

    @api.depends("product_id", "purchase_price", "product_uom_qty", "price_unit", "price_subtotal")
    def _compute_margin_percentage(self):
        """Same margin but we return a percentage from the purchase price."""
        for line in self:
            currency = line.order_id.pricelist_id.currency_id

            if not line.product_uom_qty:
                line.margin_percentage = 0.0
                continue

            if currency.is_zero(line.price_unit) or currency.is_zero(line.price_subtotal):
                line.margin_percentage = -100.0
                continue

            purchase_price = line.purchase_price or line.product_id.standard_price
            if currency.is_zero(purchase_price):
                line.margin_percentage = 100.0
                continue

            line.margin_percentage = currency.round(
                (line.price_subtotal - purchase_price * line.product_uom_qty) * 100.0 / line.price_subtotal
            )
