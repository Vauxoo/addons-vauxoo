# coding: utf-8
from openerp import http
from openerp.http import request
import json
import ast


class WebsiteCommentsAsync(http.Controller):

    @http.route(['/get_customer_purchased'],
                type='http',
                auth="public",
                website=True)
    def products_per_attr(self, **post):
        """This method main purpose is to get asynchronously all the wether the
        customer purchased or not the product he commented.
        """
        cr, uid, pool = request.cr, request.uid, request.registry
        author_ids = ast.literal_eval(post.get('author_ids'))
        product_id = int(post.get('product_id'))
        product_obj = pool.get('product.template')
        res = product_obj.comment_bought(
            cr, uid, product_id, tuple(author_ids))
        return request.make_response(json.dumps(res))
