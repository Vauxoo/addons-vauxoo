# coding: utf-8
from openerp import http
from openerp.http import request
import json


class WebsiteAsync(http.Controller):

    @http.route(['/get_prods'],
                type='http',
                auth="public",
                website=True)
    def products_per_attr(self, **post):
        """This method main purpose is to get asynchronously all the quantity of
        products per attribute on a given category.
        """
        cr, uid, pool = request.cr, request.uid, request.registry
        category_obj = pool.get('product.public.category')
        prods_per_attr = category_obj._get_async_values(
            cr, uid, post.get('category'))
        return request.make_response(json.dumps(prods_per_attr))

    @http.route(['/get_ranges'],
                type='http',
                auth="public",
                website=True)
    def products_per_range(self, **post):
        """This method main purpose is to get asynchronously all the quantity of
        products per price range on a given category.
        """
        cr, uid, pool = request.cr, request.uid, request.registry
        category_obj = pool.get('product.public.category')
        response = category_obj._get_async_ranges(
            cr, uid, post.get('category'))
        return request.make_response(json.dumps(response))
