from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def _get_price_unit(self):
        """Take into account custom rate date, if provided"""
        line = self.purchase_line_id
        if (not self.picking_id.exchange_rate_date or not line or self.product_id != line.product_id
                or line.currency_id == line.company_id.currency_id):
            return super()._get_price_unit()
        price_unit = line.price_unit
        if line.taxes_id:
            price_unit = line.taxes_id.with_context(round=False).compute_all(
                price_unit, currency=line.currency_id, quantity=1.0)['total_excluded']
        if line.product_uom.id != line.product_id.uom_id.id:
            price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
        price_unit = line.currency_id._convert(
            price_unit,
            line.company_id.currency_id,
            line.company_id,
            self.picking_id.exchange_rate_date,
            round=False)
        return price_unit
