# coding: utf-8
from openerp import http
from openerp.http import request


class WebsiteAsync(http.Controller):

    @http.route(['/get_other_purchased_products'],
                type='http',
                auth="public",
                website=True)
    def get_op_products(self, **post):
        cr, uid, pool = request.cr, request.uid, request.registry
        offset = post.get('offset', 0)
        max_product_qty = post.get('max_product_qty', 0)
        product_id = int(post.get('product_id', 0))
        prod_tmpl_id = pool.get(
            'product.product').browse(cr, uid, product_id).product_tmpl_id.id
        products = pool.get(
            'product.template')._get_purchased(cr, uid, prod_tmpl_id, offset,
                                               max_product_qty)
        view = 'website_customer_also_purchased.customer_purchased_items'
        values = {
            'products': products,
        }
        return request.website.render(view, values)
