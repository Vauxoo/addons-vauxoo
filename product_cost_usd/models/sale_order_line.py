from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("product_id", "company_id", "currency_id", "product_uom")
    def _compute_purchase_price(self):
        """Inherited to recalculate purchase price when pricelist item is
        based on cost in USD.
        """
        res = super()._compute_purchase_price()
        for line in self:
            pricelist = line.order_id.pricelist_id
            date = line.order_id.date_order
            if not line.product_id:
                continue
            price_rule = pricelist._compute_price_rule([(line.product_id, 1, False)])
            _price, rule = price_rule[line.product_id.id]
            suitable_rule = pricelist.item_ids.filtered(lambda x: x.id == rule)
            if not suitable_rule or suitable_rule.base != "standard_price_usd":
                continue
            currency_usd = self.env.ref("base.USD")
            to_cur = pricelist.currency_id
            purchase_price = line.product_id.standard_price_usd
            if line.product_uom != line.product_id.uom_id:
                purchase_price = line.product_id.uom_id._compute_price(purchase_price, line.product_uom)
            line.purchase_price = currency_usd._convert(purchase_price, to_cur, line.company_id, date, round=False)
        return res
