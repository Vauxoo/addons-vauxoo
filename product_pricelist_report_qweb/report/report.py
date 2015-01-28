#!/usr/bin/python
# -*- encoding: utf-8 -*-
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
from openerp.osv import osv
from openerp.addons.product.report import product_pricelist


class parser(product_pricelist.product_pricelist):
    def __init__(self, cr, uid, name, context):
        super(parser, self).__init__(cr, uid, name, context=context)

    def _get_titles(self, form):
        res = super(parser, self)._get_titles(form)
        if form.get('margin_cost') or form.get('margin_sale'):
            res.append({'cost': 'Cost'})
        if form.get('margin_cost'):
            res.append({'margin_cost': 'Exp. Marg. Cost'})
        if form.get('margin_sale'):
            res.append({'margin_sale': 'Exp. Marg. Sale'})
        return res

    def _get_categories(self, products, form):

        res = super(parser, self)._get_categories(products, form)
        if not form.get('margin_cost') and not form.get('margin_sale'):
            return res
        prod_obj = self.pool.get('product.product')
        cr, uid = self.cr, self.uid
        context = self.localcontext
        new_res = []
        for cat in res:
            new_products = []
            for pro_dict in cat['products']:
                new_val = pro_dict.copy()
                prod_read = prod_obj.read(
                    cr, uid, pro_dict['id'], ['standard_price'], load=None,
                    context=context)
                new_val['cost'] = prod_read['standard_price']
                new_products.append(new_val)
            new_res.append({'name': cat['name'], 'products': new_products})
        return new_res

    def _get_price(self, pricelist_id, product_id, qty):
        context = self.localcontext
        if not context.get('xls_report'):
            return super(parser, self)._get_price(pricelist_id, product_id,
                                                  qty)
        sale_price_digits = self.get_digits(dp='Product Price')
        price_dict = self.pool.get('product.pricelist').price_get(
            self.cr, self.uid, [pricelist_id], product_id, qty,
            context=context)
        if price_dict[pricelist_id]:
            price = self.formatLang(price_dict[pricelist_id],
                                    digits=sale_price_digits)
        else:
            res = self.pool.get('product.product').read(self.cr, self.uid,
                                                        [product_id])
            price = self.formatLang(res[0]['list_price'],
                                    digits=sale_price_digits)
        return price


class product_pricelist_report_qweb(osv.AbstractModel):

    # As we are inheriting a report that was previously a particular report we
    # have to keep it like that, i.e., we will keep _name the same than the
    # original

    # _name = `report.` + `report_name` (FQN)
    # report_name="product.report_pricelist"
    _name = 'report.product.report_pricelist'

    # this inheritance will allow to render this particular report
    # here old report class is being reused
    _inherit = 'report.product.report_pricelist'
    # new template will be used this because we want something more customized
    _template = 'product_pricelist_report_qweb.report_template'
    # old wrapper class from original report will be used
    # so we can comment this attribute
    _wrapped_report_class = parser

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
