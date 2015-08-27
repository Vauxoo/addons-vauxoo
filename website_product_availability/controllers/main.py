# -*- coding: utf-8 -*-
from openerp.http import request
from openerp.addons.web import http
from openerp.addons.website_sale.controllers.main import website_sale


class WebsiteSaleInh(website_sale):

    def get_attribute_value_ids(self, product):
        cr, uid, context, pool = request.cr, request.uid, request.context,\
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
                days = supplier_obj.browse(cr, uid, supplier_ids,
                                           context)[0].delay
            else:
                days = 0
            ret.append(int(days))
            new_res.append(ret)
        print "override---", new_res
        return new_res

    @http.route(
        ['/shop/product/<model("product.template"):product>'],
        type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        # import pdb; pdb.set_trace()
        result = super(WebsiteSaleInh, self).product(
            product, category, search, **kwargs)
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        template_obj = pool['product.template']
        variat_obj = pool['product.product']

        product_variants_ids = variat_obj.search(
            cr, uid, [('product_tmpl_id', '=', product.id)], context=context)
        product_variants = variat_obj.browse(
            cr, uid, product_variants_ids, context=context)

        optional_product_ids = []
        for p in product.optional_product_ids:
            ctx = dict(context, active_id=p.id)
            optional_product_ids.append(template_obj.browse(
                cr, uid, p.id, context=ctx))

        result.qcontext['optional_product_ids'] = optional_product_ids
        result.qcontext['product_variants'] = product_variants
        return result
