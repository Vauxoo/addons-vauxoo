# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class website_sale_inh(website_sale):

    def checkout_values(self, data=None):
        cr, uid, context, registry =\
            request.cr, request.uid, request.context, request.registry
        orm_partner = registry.get('res.partner')
        orm_user = registry.get('res.users')
        orm_country = registry.get('res.country')
        state_orm = registry.get('res.country.state')

        country_ids = orm_country.search(cr, SUPERUSER_ID, [], context=context)
        countries = orm_country.browse(cr, SUPERUSER_ID, country_ids, context)
        states_ids = state_orm.search(cr, SUPERUSER_ID, [], context=context)
        states = state_orm.browse(cr, SUPERUSER_ID, states_ids, context)
        partner = orm_user.browse(
            cr,
            SUPERUSER_ID,
            request.uid,
            context).partner_id

        order = None

        shipping_id = None
        shipping_ids = []
        checkout = {}
        if not data:
            if request.uid != request.website.user_id.id:
                checkout.update(self.checkout_parse("billing", partner))
                shipping_ids = orm_partner.search(
                    cr, SUPERUSER_ID, [
                        ("parent_id", "=", partner.id),
                        ('type', "=", 'delivery')], context=context)
            else:
                order = request.website.sale_get_order(
                    force_create=1,
                    context=context)
                if order.partner_id:
                    domain = [("partner_id", "=", order.partner_id.id)]
                    user_ids = request.registry['res.users'].search(
                        cr,
                        SUPERUSER_ID,
                        domain,
                        context=dict(
                            context or {},
                            active_test=False))
                    if not user_ids or request.website.user_id.id not in user_ids:  # noqa
                        checkout.update(
                            self.checkout_parse(
                                "billing",
                                order.partner_id))
        else:
            checkout = self.checkout_parse('billing', data)
            try:
                shipping_id = int(data["shipping_id"])
            except ValueError:
                pass
            if shipping_id == -1:
                checkout.update(self.checkout_parse('shipping', data))

        if shipping_id is None:
            if not order:
                order = request.website.sale_get_order(context=context)
            if order and order.partner_shipping_id:
                shipping_id = order.partner_shipping_id.id

        shipping_ids = list(set(shipping_ids) - set([partner.id]))

        if shipping_id == partner.id:
            shipping_id = 0
        elif shipping_id > 0 and shipping_id not in shipping_ids:
            shipping_ids.append(shipping_id)
        elif shipping_id is None and shipping_ids:
            shipping_id = shipping_ids[0]

        ctx = dict(context, show_address=1)
        shippings = []
        if shipping_ids:
            shippings = shipping_ids and orm_partner.browse(
                cr,
                SUPERUSER_ID,
                list(shipping_ids),
                ctx) or []
        if shipping_id > 0:
            shipping = orm_partner.browse(cr, SUPERUSER_ID, shipping_id, ctx)
            checkout.update(self.checkout_parse("shipping", shipping))

        checkout['shipping_id'] = shipping_id

        # Default search by user country
        if not checkout.get('country_id'):
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                country_ids = request.registry.get('res.country').search(
                    cr, uid, [
                        ('code', '=', country_code)], context=context)
                if country_ids:
                    checkout['country_id'] = country_ids[0]
        checkout['mobile'] = partner.mobile
        values = {
            'countries': countries,
            'states': states,
            'checkout': checkout,
            'shipping_id': partner.id != shipping_id and shipping_id or 0,
            'shippings': shippings,
            'error': {},
            'has_check_vat': hasattr(registry['res.partner'], 'check_vat')
        }

        return values

    def checkout_form_save(self, checkout):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry  # noqa

        order = request.website.sale_get_order(force_create=1, context=context)

        orm_partner = registry.get('res.partner')
        orm_user = registry.get('res.users')
        order_obj = request.registry.get('sale.order')

        partner_lang = request.lang if request.lang in [
            lang.code for lang in request.website.language_ids] else None

        billing_info = {}
        if partner_lang:
            billing_info['lang'] = partner_lang
        billing_info.update(self.checkout_parse('billing', checkout, True))

        # set partner_id
        partner_id = None
        if request.uid != request.website.user_id.id:
            partner_id = orm_user.browse(
                cr,
                SUPERUSER_ID,
                uid,
                context=context).partner_id.id
        elif order.partner_id:
            user_ids = request.registry['res.users'].search(
                cr, SUPERUSER_ID, [
                    ("partner_id", "=", order.partner_id.id)], context=dict(
                    context or {}, active_test=False))
            if not user_ids or request.website.user_id.id not in user_ids:
                partner_id = order.partner_id.id

        # save partner informations
        if partner_id and request.website.partner_id.id != partner_id:
            orm_partner.write(
                cr,
                SUPERUSER_ID,
                [partner_id],
                billing_info,
                context=context)
        else:
            # create partner
            partner_id = orm_partner.create(
                cr,
                SUPERUSER_ID,
                billing_info,
                context=context)

        # create a new shipping partner
        if checkout.get('shipping_id') == -1:
            shipping_info = {}
            if partner_lang:
                shipping_info['lang'] = partner_lang
            shipping_info.update(
                self.checkout_parse(
                    'shipping',
                    checkout,
                    True))
            shipping_info['type'] = 'delivery'
            shipping_info['parent_id'] = partner_id
            checkout['shipping_id'] = orm_partner.create(
                cr,
                SUPERUSER_ID,
                shipping_info,
                context)

        order_info = {
            'partner_id': partner_id,
            'message_follower_ids': [(4, partner_id), (3, request.website.partner_id.id)],
            'partner_invoice_id': partner_id,
        }
        order_info.update(
            order_obj.onchange_partner_id(
                cr,
                SUPERUSER_ID,
                [],
                partner_id,
                context=context)['value'])
        address_change = order_obj.onchange_delivery_id(
            cr,
            SUPERUSER_ID,
            [],
            order.company_id.id,
            partner_id,
            checkout.get('shipping_id'),
            None,
            context=context)['value']
        order_info.update(address_change)
        if address_change.get('fiscal_position'):
            fiscal_update = order_obj.onchange_fiscal_position(
                cr, SUPERUSER_ID, [], address_change['fiscal_position'], [
                    (4, l.id) for l in order.order_line], context=None)['value']
            order_info.update(fiscal_update)

        order_info.pop('user_id')
        order_info.update(
            partner_shipping_id=checkout.get('shipping_id') or partner_id)

        order_obj.write(
            cr, SUPERUSER_ID, [
                order.id], order_info, context=context)
