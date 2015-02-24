# -*- coding: utf-8 -*-
import werkzeug
from openerp import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class website_sale(website_sale):

    def get_attribute_value_ids(self, product):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        product_obj = pool['product.product']
        res = super(website_sale, self).get_attribute_value_ids(product)
        new_res = []
        for r in res:
            stock_state = product_obj.browse(cr, uid, [r[0]], context)[0].stock_state
            r.append(int(stock_state))
            new_res.append(r)
        return new_res
