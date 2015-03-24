# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request


class website_customers_purchased(http.Controller):

    @http.route(['/shop/product/'],
                type='http', auth='public', website=True)
    def customers_purchased(self, **post):
        print "ROUTE PASSED"
        request.cr.execute("""
            select product_id, count(product_id) as p_count
            from sale_order_line
            where order_id in (select order_id
                               from sale_order_line
                               where product_id = 11) and product_id <> 11
            group by product_id
            order by p_count;
            """)
        for row in request.cr.fetchall():
            print row
        values = 'p'
        return values
