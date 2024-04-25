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
