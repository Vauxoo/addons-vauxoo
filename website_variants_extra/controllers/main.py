# -*- coding: utf-8 -*-
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.http import request


class WebsiteSaleInh(website_sale):

    def get_attribute_value_ids(self, product):
        cr, uid, context, pool = request.cr, request.uid, request.context,\
            request.registry
        product_obj = pool['product.product']
        res = super(WebsiteSaleInh, self).get_attribute_value_ids(product)
        new_res = []
        for ret in res:
            stock_state = product_obj.browse(cr, uid, [ret[0]],
                                             context)[0].stock_state
            ret.append(int(stock_state))
            new_res.append(ret)
        return new_res
