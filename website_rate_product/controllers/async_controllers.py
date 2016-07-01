# coding: utf-8
from openerp import http
from openerp.http import request
import json


class WebsiteAsync(http.Controller):

    @http.route(['/get_comments_qty'],
                type='http',
                auth="public",
                website=True)
    def comments_per_product(self, **post):
        cr, uid, pool = request.cr, request.uid, request.registry
        message_qty = pool.get(
            'mail.message')._get_product_comments_qty(cr,
                                                      uid,
                                                      post.get('product_id'))
        return request.make_response(json.dumps(message_qty))
