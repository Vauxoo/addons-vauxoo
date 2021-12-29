from odoo import http

from odoo.addons.account.controllers.portal import PortalAccount as PA
from odoo.addons.sale.controllers.portal import CustomerPortal as CP


class CustomerPortal(CP):
    def _totals_by_currency(self, records):
        """Compute total amounts for invoices and sale orders, grouped by currency"""
        if not records:
            return {}
        currencies = records.currency_id
        totals_by_currency = {
            currency: {
                "amount": 0.0,
            }
            for currency in currencies
        }
        for record in records.filtered(lambda inv: inv.state not in ("draft", "cancel")):
            totals_this_currency = totals_by_currency[record.currency_id]
            totals_this_currency["amount"] += record.amount_total
            if "amount_residual" in record:
                totals_this_currency.setdefault("unpaid", 0.0)
                totals_this_currency.setdefault("paid", 0.0)
                totals_this_currency["unpaid"] += record.amount_residual
                totals_this_currency["paid"] += record.amount_total - record.amount_residual

        return totals_by_currency

    @http.route(["/my/quotes", "/my/quotes/page/<int:page>"], type="http", auth="user", website=True)
    def portal_my_quotes(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        response = super().portal_my_quotes(page=page, date_begin=date_begin, date_end=date_end, sortby=sortby, **kw)
        quotations = response.qcontext.get("quotations")
        response.qcontext["totals_by_currency"] = self._totals_by_currency(quotations)
        return response

    @http.route(["/my/orders", "/my/orders/page/<int:page>"], type="http", auth="user", website=True)
    def portal_my_orders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        response = super().portal_my_orders(page=page, date_begin=date_begin, date_end=date_end, sortby=sortby, **kw)
        orders = response.qcontext.get("orders")
        response.qcontext["totals_by_currency"] = self._totals_by_currency(orders)
        return response


class PortalAccount(PA):
    @http.route(["/my/invoices", "/my/invoices/page/<int:page>"], type="http", auth="user", website=True)
    def portal_my_invoices(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        response = super().portal_my_invoices(
            page=page, date_begin=date_begin, date_end=date_end, sortby=sortby, filterby=filterby, **kw
        )
        invoices = response.qcontext.get("invoices")
        response.qcontext["totals_by_currency"] = self._totals_by_currency(invoices)
        return response
