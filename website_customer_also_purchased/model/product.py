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

from openerp import api, models
from openerp.http import request


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _best_sell_sort(self, product_tmp, offset=0, max_product_qty=6):
        variants_ids = '(%s)' % ', '.join(
            [str(v.id) for v in product_tmp.product_variant_ids])
        if variants_ids and variants_ids != '()':
            query = "\
                SELECT p.product_tmpl_id from sale_order_line sol \
                join sale_order_line sol2 on sol.order_id=sol2.order_id \
                join product_product p on sol2.product_id = p.id \
                join product_template p_tmpl on p.product_tmpl_id=p_tmpl.id \
                where sol.product_id in {0} and p.product_tmpl_id != {1} \
                and p_tmpl.website_published=True \
                group by p.product_tmpl_id \
                order by count(sol2.product_id) desc LIMIT {2} OFFSET {3};\
                    ".format(variants_ids, product_tmp.id,
                             int(max_product_qty), int(offset))
            product_tmp._cr.execute(query)
            other_products = product_tmp._cr.fetchall()
            result = []
            for op in other_products:
                result.append(op[0])
            return result

    @api.multi
    def _get_purchased(self, offset=0, max_product_qty=6):

        """
        This method gets all the products that were purchased in the
        same sale order og the current product.
        """
        self.ensure_one()
        sort = request.httprequest.cookies.get('cap_sort', False)
        product_list = []
        if sort == 'best_seller':
            product_list = self._best_sell_sort(self,
                                                offset, max_product_qty)
        return self.browse(product_list)
