# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# #############Credits#########################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your
#    option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
from __future__ import division
from odoo import models
from odoo.tools import float_round


class ReportPricelist(models.AbstractModel):

    _inherit = 'report.product.report_pricelist'

    def _get_dict_titles(self, form):
        titles_list = self._get_titles(form)
        titles = {}
        for title in titles_list:
            titles.update(title)
        return titles

    def _get_titles(self, form):
        res = super(ReportPricelist, self)._get_titles(form)
        if form.get('margin_cost') or form.get('margin_sale'):
            res.append({'cost': 'Cost'})
        if form.get('margin_cost'):
            res.append({'margin_cost': 'Exp. Marg. Cost (%)'})
        if form.get('margin_sale'):
            res.append({'margin_sale': 'Exp. Marg. Sale (%)'})
        return res

    def _get_categories(self, pricelist, products, quantities):
        res = super(ReportPricelist, self)._get_categories(pricelist, products, quantities)

        if not self._context.get('margin_cost') and not self._context.get('margin_sale'):
            return res

        for categories in res:
            for product in categories['products']:
                cost = product.standard_price
                qty1 = categories['prices'][product.id][1]
                categories['prices'][product.id].update({
                    'margin_cost': qty1 and ((qty1 - cost) * 100 / qty1) or 0.0,
                    'margin_sale': cost and ((qty1 - cost) * 100 / cost) or 0.0,
                })

        return res

    def _get_price(self, pricelist, product, qty):
        sale_price_digits = self.env['decimal.precision'].precision_get('Product Price')
        price = pricelist.get_product_price(product, qty, False)
        if not price and not self._context.get('only_prod_pricelist'):
            price = product.list_price
        return float_round(price, precision_digits=sale_price_digits)
