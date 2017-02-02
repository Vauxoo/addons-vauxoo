# coding: utf-8
import datetime
from odoo.http import request
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import SUPERUSER_ID


class WebsiteSaleInh(WebsiteSale):

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
        warehouse_obj = pool['stock.warehouse']
        warehouse_ids = warehouse_obj.search(
            cr, uid, [('website_published', '=', True)], context=context)
        warehouses = warehouse_obj.browse(
            cr, uid, warehouse_ids, context=context)

        res = super(WebsiteSaleInh, self).get_attribute_value_ids(product)
        new_res = []
        for ret in res:
            location_list = self.get_stock_quants([ret[0]], warehouses)
            ret.append(location_list)
            new_res.append(ret)
        return new_res

    def get_stock_quants(self, variants_ids, warehouses):
        cr, uid, context, pool = request.cr, SUPERUSER_ID, request.context,\
            request.registry
        purchase_l_obj = pool['purchase.order.line']
        product_obj = pool['product.product']
        res = []
        for warehouse in warehouses:
            context.update({'warehouse': warehouse.id})
            products = product_obj.browse(cr, uid, variants_ids, context)
            for product in products:
                stock_state = '2'
                for route in product.route_ids:
                    if route.consider_on_request:
                        stock_state = '4'
                        break
                if stock_state != '4':
                    stock_state = product._get_availability_by_qty()
                p_lines_ids = purchase_l_obj.search(
                    cr, uid, [('product_id', '=', product.id),
                              ('state', 'in', ('draft', 'confirmed')),
                              ('order_id.picking_type_id.warehouse_id',
                               '=', warehouse.id)], context=context)
                purchase_lines = purchase_l_obj.browse(
                    cr, uid, p_lines_ids, context=context)
                dates_planed = [
                    datetime.datetime.strptime(
                        line.date_planned, '%Y-%m-%d').date()
                    for line in purchase_lines]
                date = dates_planed and min(dates_planed) or 'unknown'
                res.append([warehouse.stock_alias, stock_state, str(date)])
        return res

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
