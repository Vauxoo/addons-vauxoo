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


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _best_sell_sort(self, product_tmp, offset=0, max_product_qty=6):
        variants_ids = product_tmp.product_variant_ids._ids
        query = "\
            SELECT p.product_tmpl_id from sale_order_line sol \
            join sale_order_line sol2 on sol.order_id=sol2.order_id \
            join product_product p on sol2.product_id = p.id \
            join product_template p_tmpl on p.product_tmpl_id=p_tmpl.id \
            where sol.product_id in %s and p.product_tmpl_id != %s \
            and p_tmpl.website_published=True \
            group by p.product_tmpl_id \
            order by count(sol2.product_id) desc LIMIT %s OFFSET %s;"
        product_tmp._cr.execute(query, (variants_ids, product_tmp.id,
                                        max_product_qty, offset))
        other_products = product_tmp._cr.fetchall()
        return [op[0] for op in other_products]

    @api.multi
    def _get_purchased(self, offset=0, max_product_qty=6):

        """
        This method gets all the products that were purchased in the
        sale order of the current product.The returned product are sorted
        according to website configuration.
        """
        self.ensure_one()
        sort = self.env['website'].get_current_website().cap_sort
        product_list = []
        if sort == 'best_seller':
            product_list = self._best_sell_sort(self,
                                                offset, max_product_qty)
        return self.browse(product_list)
