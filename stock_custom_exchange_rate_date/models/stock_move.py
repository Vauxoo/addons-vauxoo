from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_price_unit(self):
        """Take into account custom rate date, if provided"""
        line = self.purchase_line_id
        if (
            not self.picking_id.exchange_rate_date
            or self.product_id != line.product_id
            or line.currency_id == line.company_id.currency_id
            or self._should_ignore_pol_price()
        ):
            return super()._get_price_unit()
        price_unit = line._get_gross_price_unit()
        price_unit = line.currency_id._convert(
            price_unit, line.company_id.currency_id, line.company_id, self.picking_id.exchange_rate_date, round=False
        )
        return price_unit
