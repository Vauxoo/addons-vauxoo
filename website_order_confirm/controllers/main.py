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
        email_act = None
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
            if not order.amount_total and not tx:
                # Orders are confirmed by payment transactions, but there is
                # none for free orders,
                # (e.g. free events), so confirm immediately
                order.action_button_confirm()
            # send by email
            email_act = sale_order_obj.action_quotation_send(
                cr, SUPERUSER_ID, [
                    order.id], context=request.context)
            order.action_button_confirm()
        elif tx and tx.state == 'cancel':
            # cancel the quotation
            sale_order_obj.action_cancel(
                cr, SUPERUSER_ID, [
                    order.id], context=request.context)

        # send the email
        if email_act and email_act.get('context'):
            composer_obj = request.registry['mail.compose.message']
            composer_values = {}
            email_ctx = email_act['context']
            template_values = [
                email_ctx.get('default_template_id'),
                email_ctx.get('default_composition_mode'),
                email_ctx.get('default_model'),
                email_ctx.get('default_res_id'),
            ]
            composer_values.update(
                composer_obj.onchange_template_id(
                    cr,
                    SUPERUSER_ID,
                    None,
                    *template_values,
                    context=context).get(
                    'value',
                    {}))
            if not composer_values.get(
                    'email_from') and uid == request.website.user_id.id:
                composer_values[
                    'email_from'] = request.website.user_id.company_id.email
            for key in ['attachment_ids', 'partner_ids']:
                if composer_values.get(key):
                    composer_values[key] = [(6, 0, composer_values[key])]
            composer_id = composer_obj.create(
                cr,
                SUPERUSER_ID,
                composer_values,
                context=email_ctx)
            composer_obj.send_mail(
                cr,
                SUPERUSER_ID,
                [composer_id],
                context=email_ctx)

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset(context=context)

        return request.redirect('/shop/confirmation')
