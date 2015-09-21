# coding: utf-8
from openerp.http import request
from openerp.addons.web import http
from openerp.addons.website_sale.controllers.main import website_sale
from openerp import SUPERUSER_ID

import datetime


class WebsiteSaleInh(website_sale):

    def get_attribute_value_ids(self, product):
        cr, uid, context, pool = request.cr, SUPERUSER_ID, request.context,\
            request.registry
        product_obj = pool['product.product']
        supplier_obj = pool['product.supplierinfo']
        res = super(WebsiteSaleInh, self).get_attribute_value_ids(product)
        new_res = []
        for ret in res:
            product_cache = product_obj.browse(cr, uid, [ret[0]], context)[0]
            stock_state = product_cache.stock_state
            ret.append(int(stock_state))
            p_tmpl_id = product_cache.product_tmpl_id.id
            supplier_ids = supplier_obj.search(cr, uid,
                                               [('product_tmpl_id', '=',
                                                 p_tmpl_id)],
                                               limit=1,
                                               order='sequence asc')
            if supplier_ids:
                delay_days = supplier_obj.browse(cr, uid, supplier_ids,
                                                 context)[0].delay
                day = datetime.datetime.now() + datetime.timedelta(
                    days=delay_days)
                days = day.strftime("%Y/%m/%d")
                days = days.split('/')
                days = [int(i) for i in days]
            else:
                days = 0
            ret.append(days)
            new_res.append(ret)
        return new_res

    def get_locations_variant_ids(self, product):
        cr, uid, context, pool = request.cr, SUPERUSER_ID, request.context,\
            request.registry
        product_obj = pool['product.product']
        lct_ids = pool['stock.location'].search(
            cr, uid, [('website_published', '=', True)], context=context)
        lct_published_brw = pool['stock.location'].browse(
            cr, uid, lct_ids, context=context)
        res = super(WebsiteSaleInh, self).get_attribute_value_ids(product)
        new_res = []
        for ret in res:
            product_cache = product_obj.browse(cr, uid, [ret[0]], context)[0]
            location_list = [
                (self.get_stock_quants(product_cache, location))
                for location in lct_published_brw]
            ret.append(location_list)
            new_res.append(ret)
        return new_res

    def get_stock_quants(self, product, location):
        cr, uid, context, pool = request.cr, SUPERUSER_ID, request.context,\
            request.registry
        qty = product.with_context(
            location=location.id)._product_available(None, False)
        new_qty = qty.get(product.id).get('qty_available')
        stock_state = '2'
        for route in product.route_ids:
            if route.consider_on_request:
                stock_state = '4'
                break
        if stock_state != '4':
            if new_qty > product.low_stock:
                stock_state = '1'
            elif 0 < new_qty <= product.low_stock:
                stock_state = '3'
            elif new_qty <= 0:
                stock_state = '2'
        porl_ids = pool['purchase.order.line'].search(
            cr, uid,
            [('product_id', '=', product.id),
             ('state', 'in', ('draft', 'confirmed')),
             ('order_id.picking_type_id.default_location_dest_id',
                '=', location.id)
             ], context=context)
        purchase_lines = pool['purchase.order.line'].browse(
            cr, uid, porl_ids, context=context)
        dates_planed = [
            datetime.datetime.strptime(line.date_planned, '%Y-%m-%d').date()
            for line in purchase_lines]
        if dates_planed:
            date = min(dates_planed)
        else:
            date = 'unknown'
        return [location.stock_alias, stock_state, str(date)]

    @http.route(
        ['/shop/product/<model("product.template"):product>'],
        type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        result = super(WebsiteSaleInh, self).product(
            product, category, search, **kwargs)
        cr, uid, context, pool = request.cr, SUPERUSER_ID, request.context,\
            request.registry
        variat_obj = pool['product.product']
        product_variants_ids = variat_obj.search(
            cr, uid, [('product_tmpl_id', '=', product.id)], context=context)
        product_variants = variat_obj.browse(
            cr, uid, product_variants_ids, context=context)
        result.qcontext['product_variants'] = product_variants
        result.qcontext[
            'get_locations_variant_ids'] = self.get_locations_variant_ids
        return result
