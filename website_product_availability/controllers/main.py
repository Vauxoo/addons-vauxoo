# -*- coding: utf-8 -*-
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class website_sale(website_sale):

    def get_attribute_value_ids(self, product):
        cr, uid, context, pool = request.cr, request.uid, request.context,\
            request.registry
        product_obj = pool['product.product']
        supplier_obj = pool['product.supplierinfo']
        res = super(website_sale, self).get_attribute_value_ids(product)
        new_res = []
        for r in res:
            product_cache = product_obj.browse(cr, uid, [r[0]], context)[0]
            stock_state = product_cache.stock_state
            r.append(int(stock_state))
            new_res.append(r)
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
            r.append(int(days))
            new_res.append(r)
        return new_res
