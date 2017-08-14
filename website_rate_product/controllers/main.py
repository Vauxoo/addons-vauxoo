# coding: utf-8
import werkzeug
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import login_and_redirect
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleInh(WebsiteSale):

    @http.route(['/shop/product/comment/<int:product_template_id>'],
                type='http', auth="public", methods=['POST'], website=True)
    def product_comment(self, product_template_id, **post):
        if not request.session.uid:
            return login_and_redirect()
        cr, uid, context = request.cr, request.uid, request.context
        if post.get('comment'):
            mid = request.registry['product.template'].message_post(
                cr, uid, product_template_id,
                body=post.get('comment'),
                message_type='comment',
                subtype='mt_comment',
                context=dict(context, mail_create_nosubscribe=True))
        if post.get('rating', 0):
            data = {
                'rating': int(post.get('rating')),
            }
            request.registry['mail.message'].write(cr, uid, [mid], data,
                                                   context)
        res = werkzeug.utils.redirect(request.httprequest.referrer +
                                      "#comments")
        return res
