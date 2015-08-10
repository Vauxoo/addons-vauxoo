# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale
import re


class WebsiteSaleInh(website_sale):

    def checkout_values(self, data=None):
        cr, uid, context, registry =\
            request.cr, request.uid, request.context, request.registry
        orm_partner = registry.get('res.partner')
        orm_user = registry.get('res.users')
        orm_country = registry.get('res.country')
        orm_city = registry.get('res.better.zip')
        state_orm = registry.get('res.country.state')
        sale_order_obj = registry.get('sale.order')

        country_ids = orm_country.search(cr, SUPERUSER_ID, [], context=context)
        countries = orm_country.browse(cr, SUPERUSER_ID, country_ids, context)
        city_ids = orm_city.search(cr, SUPERUSER_ID, [], context=context)
        cities = orm_city.browse(cr, SUPERUSER_ID, city_ids, context)
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
            checkout['mobile'] = partner.mobile
            checkout['is_company'] = partner.is_company
        else:
            order_to_update = request.website.sale_get_order(context=context)
            sale_order_obj.write(cr, SUPERUSER_ID, [order_to_update.id],
                                 {'comments': data.get('comments', None)},
                                 context=context)
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

        values = {
            'cities': cities,
            'countries': countries,
            'states': states,
            'checkout': checkout,
            'shipping_id': partner.id != shipping_id and shipping_id or 0,
            'shippings': shippings,
            'error': {},
            'has_check_vat': hasattr(registry['res.partner'], 'check_vat')
        }

        return values

    mandatory_billing_fields = [
        "name", "phone", "email", "street2", "zip_id", "country_id"]
    optional_billing_fields = [
        "street",
        "state_id",
        "vat", "vat_subjected", "zip", "mobile", "is_company", "zip_id"]
    mandatory_shipping_fields = [
        "name", "phone", "street", "country_id"]
    optional_shipping_fields = ["state_id", "zip"]

    def checkout_parse(self, address_type, data, remove_prefix=False):
        """ data is a dict OR a partner browse record
        """
        # set mandatory and optional fields
        assert address_type in ('billing', 'shipping')
        if address_type == 'billing':
            all_fields = self.mandatory_billing_fields + self.optional_billing_fields  # noqa
            prefix = ''
        else:
            all_fields = self.mandatory_shipping_fields + self.optional_shipping_fields  # noqa
            prefix = 'shipping_'

        # set data
        if isinstance(data, dict):
            query = dict((prefix + field_name, data[prefix + field_name])
                for field_name in all_fields if prefix + field_name in data)  # noqa
        else:
            query = dict((prefix + field_name, getattr(data, field_name))
                for field_name in all_fields if getattr(data, field_name))  # noqa
            if address_type == 'billing' and data.parent_id:
                query[prefix + 'street'] = data.parent_id.name

        if query.get(prefix + 'state_id'):
            query[prefix + 'state_id'] = int(query[prefix + 'state_id'])
        if query.get(prefix + 'country_id'):
            query[prefix + 'country_id'] = int(query[prefix + 'country_id'])
        if query.get(prefix + 'zip_id'):
            query[prefix + 'zip_id'] = int(query[prefix + 'zip_id'])
        if query.get(prefix + 'mobile'):
            query[prefix + 'mobile'] = int(query[prefix + 'mobile'])
        if query.get(prefix + 'is_company'):
            query[prefix + 'is_company'] = query[prefix + 'is_company']
        else:
            query[prefix + 'is_company'] = False

        if query.get(prefix + 'vat'):
            query[prefix + 'vat_subjected'] = True

        if not remove_prefix:
            return query

        return dict((field_name, data[prefix + field_name]) for field_name in all_fields if prefix + field_name in data)  # noqa

    # This is a simple function that validates special fields as: email, vat...
    def checkout_form_validate(self, data):
        cr, uid, registry = request.cr, request.uid, request.registry

        # Validation
        error = dict()
        for field_name in self.mandatory_billing_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'

        if data.get("vat") and hasattr(registry["res.partner"], "check_vat"):
            if request.website.company_id.vat_check_vies:
                # force full VIES online check
                check_func = registry["res.partner"].vies_vat_check
            else:
                # quick and partial off-line checksum validation
                check_func = registry["res.partner"].simple_vat_check
            vat_country, vat_number = registry["res.partner"]._split_vat(data.get("vat"))  # noqa
            if not check_func(cr, uid, vat_country, vat_number, context=None):
                error["vat"] = 'error'

        if data.get("shipping_id") == -1:
            for field_name in self.mandatory_shipping_fields:
                field_name = 'shipping_' + field_name
                if not data.get(field_name):
                    error[field_name] = 'missing'
        if data.get('email'):
            if not re.match(r"[^@]+@[^@]+\.[^@]+", data.get('email')):
                error["email"] = 'invalid'
        return error
