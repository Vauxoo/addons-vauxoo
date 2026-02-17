from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("product_id", "company_id", "currency_id", "product_uom_id")
    def _compute_purchase_price(self):
        """Inherited to recalculate purchase price when pricelist item is
        based on cost in USD.
        """
        res = super()._compute_purchase_price()
        for line in self:
            line = line.with_company(line.company_id)
            product = line.product_id
            if not product:
                continue
            pricelist = line.order_id.pricelist_id
            date = line.order_id.date_order
            price_rule = pricelist._compute_price_rule(
                products=product,
                quantity=1.0,
                currency=pricelist.currency_id,
                uom=line.product_uom_id,
                date=date,
            )
            _price, rule = price_rule.get(product.id, (0.0, False))
            suitable_rule_id = self.env["product.pricelist.item"].browse(rule)
            if suitable_rule_id.base != "standard_price_usd":
                continue
            currency_usd = self.env.ref("base.USD")
            to_cur = pricelist.currency_id
            purchase_price = product.standard_price_usd
            if line.product_uom_id != product.uom_id:
                purchase_price = product.uom_id._compute_price(purchase_price, line.product_uom_id)
            line.purchase_price = currency_usd._convert(purchase_price, to_cur, line.company_id, date, round=False)
        return res
