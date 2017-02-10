# -*- coding: utf-8 -*-
# Copyright 2017 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _get_purchase_price(self, pricelist, product, product_uom, date):
        """ Inherited to recalculate purchase price when pricelist item is
        based on cost in usd.
        """
        res = super(SaleOrderLine, self)._get_purchase_price(
            pricelist, product, product_uom, date)
        product_qty = product._context.get('quantity', 1)
        product_partner = product._context.get('partner', False)
        price_rule = pricelist._compute_price_rule([
            (product, product_qty, product_partner)])
        price, rule = price_rule[product.id]
        suitable_rule = pricelist.item_ids.filtered(lambda x: x.id == rule)
        if not suitable_rule or suitable_rule.base != 'standard_price_usd':
            return res
        # TODO: fix when base is a pricelist
        frm_cur = self.env.ref('base.USD')
        to_cur = pricelist.currency_id
        purchase_price = product.standard_price_usd
        if product_uom != product.uom_id:
            purchase_price = product.uom_id._compute_price(
                purchase_price, product_uom)
        price = frm_cur.with_context(date=date).compute(
            purchase_price, to_cur, round=False)
        return {'purchase_price': price}

    @api.model
    def _compute_margin(self, order_id, product_id, product_uom_id):
        """ Inherited to recalculate purchase price when pricelist item is
        based on cost in usd.

        Why this inheritance?

        In spite of the name this method is only used to get the purchase
        price, calling the method get_purchase_price we reuse that logic to
        calculate the purchase price when pricelist item is based on cost
        in usd.
        """
        price = super(SaleOrderLine, self)._compute_margin(
            order_id, product_id, product_uom_id)
        date = order_id.date_order
        prices = self._get_purchase_price(
            order_id.pricelist_id, product_id, product_uom_id, date)

        return prices.get('purchase_price', price)

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        res = super(SaleOrderLine, self).product_uom_change()
        if not self.product_uom or not self.product_uom_qty:
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            price = self.purchase_price
            prices = self._get_purchase_price(
                self.order_id.pricelist_id, self.product_id,
                self.product_uom, self.order_id.date_order)
            self.purchase_price = prices.get('purchase_price', price)
        return res
