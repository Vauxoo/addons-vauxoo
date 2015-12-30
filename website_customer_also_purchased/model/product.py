# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)2010-  OpenERP SA (<http://openerp.com>). All Rights Reserved
#    App Author: Vauxoo
#
#    Developed by Oscar Alcala
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv
from openerp.osv import fields
from openerp import SUPERUSER_ID


class ProductTemplate(osv.osv):
    _inherit = 'product.template'

    def _get_purchased(self, cr, uid, ids, field_names, arg=None,
                       context=None):
        """
        This method gets all the products that were purchased in the
        same sale order og the current product.
        """
        result = {}
        pids_t = []
        for p_id in ids:
            result[p_id] = []
        cr.execute("""
            select id
            from product_product
            where product_tmpl_id = {0}
            """.format(ids[0]))
        pid = cr.fetchall()
        for pr in pid:
            pids_t.append(pr[0])
        pids = '(%s)' % ', '.join(map  # pylint: disable=W0141,W0110
                                  (repr,
                                   tuple(pids_t)))
        if pids and pids != '()':
            cr.execute("\
                SELECT product_tmpl_id\
                FROM product_product\
                WHERE id in (\
                select product_id\
                from sale_order_line\
                where order_id in (select order_id\
                               from sale_order_line\
                               where product_id in {0}\
                               ) and product_id not in {0}\
                group by product_id)\
                GROUP BY product_tmpl_id;\
            ".format(pids))
            res = cr.fetchall()
            for ret in res:
                if self.browse(cr, SUPERUSER_ID, [ret[0]],
                               context)[0].website_published:
                    result[ids[0]].append(ret[0])
        return result

    _columns = {
        'customer_purchased': fields.function(_get_purchased, method=True,
                                              type='one2many',
                                              relation='product.template',
                                              string="Customers Purchased")
    }
