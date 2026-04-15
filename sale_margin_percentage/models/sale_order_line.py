from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_threshold = fields.Float(
        compute="_compute_margin_threshold",
        store=True,
        readonly=False,
        help="Limit margin set in sales configuration",
    )
    margin_alert = fields.Selection(
        selection=[
            ("none", "None"),
            ("warning", "Warning"),
            ("danger", "Danger"),
        ],
        compute="_compute_margin_alert",
    )

    @api.depends("company_id")
    def _compute_margin_threshold(self):
        for line in self:
            line.margin_threshold = (line.company_id or self.env.company).margin_threshold

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

    @api.depends("margin_percent", "margin_threshold")
    def _compute_margin_alert(self):
        """Compute the margin alert level based on the margin percentage and threshold
        and avoid the warning because of the groups that can't see the margin percentage
        """
        for line in self:
            if line.margin_percent <= 0.0:
                line.margin_alert = "danger"
            elif 0.0 < line.margin_percent <= line.margin_threshold:
                line.margin_alert = "warning"
            else:
                line.margin_alert = "none"
