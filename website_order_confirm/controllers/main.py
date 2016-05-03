# coding: utf-8
from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class WebsiteSaleInh(website_sale):

    @http.route(
        '/shop/payment/validate',
        type='http',
        auth="public",
        website=True)
    def payment_validate(
            self,
            transaction_id=None,
            sale_order_id=None,
            **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        cr, uid, context = request.cr, request.uid, request.context
        sale_order_obj = request.registry['sale.order']

        if transaction_id is None:
            tx = request.website.sale_get_transaction()
        else:
            tx = request.registry['payment.transaction'].browse(
                cr,
                uid,
                transaction_id,
                context=context)

        if sale_order_id is None:
            order = request.website.sale_get_order(context=context)
        else:
            order = request.registry['sale.order'].browse(
                cr,
                SUPERUSER_ID,
                sale_order_id,
                context=context)
            assert order.id == request.session.get('sale_last_order_id')

        if not order or (order.amount_total and not tx):
            return request.redirect('/shop')

        if (not order.amount_total and not tx) or tx.state in [
                'pending', 'done']:
            # always confirm the order
            order.with_context(
                dict(context, send_mail=True)).action_button_confirm()
        elif tx and tx.state == 'cancel':
            # cancel the quotation
            sale_order_obj.action_cancel(
                cr, SUPERUSER_ID, [
                    order.id], context=request.context)
        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset(context=context)

        if tx and tx.state == 'draft':
            return request.redirect('/shop')

        return request.redirect('/shop/confirmation')
