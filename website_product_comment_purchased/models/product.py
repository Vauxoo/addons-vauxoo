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
from openerp import models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def comment_bought(self, product_id, author_ids):
        """
        This method retrieves a dictionary with two keys, `author_id` and
        `purchased` the first is the id of the author of the comment on the
        given `product_id` the second its a boolean that will be true if a
        sale order is found with partner related to the user that commented
        the product.

        :param product_id: The id of the product where the comment was posted.
        :param author_ids: A list of the authors of all the comments given on
                           the product.
        """
        res = {}
        query = """
        SELECT so.partner_id, count(sol.product_id)
        FROM sale_order_line sol
            JOIN sale_order so ON sol.order_id = so.id
            JOIN res_users ru ON ru.partner_id = so.partner_id
            JOIN product_product pp on pp.id = sol.product_id
        WHERE so.partner_id IN %s AND pp.product_tmpl_id = %s
        GROUP BY so.partner_id;
        """
        self._cr.execute(query, (author_ids, product_id))
        res = dict(self._cr.fetchall())
        to_jsonfy = [{'author_id': k, 'purchased': 1} for k in res]
        return to_jsonfy
