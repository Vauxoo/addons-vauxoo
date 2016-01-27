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
from openerp import models, fields, api
from datetime import datetime
import time
from openerp import SUPERUSER_ID


class WebsiteSeoMetadata(models.Model):
    _inherit = ["website.seo.metadata"]
    views = fields.Integer(
        'Views',
        help='This field shows the number of times a product has been'
             'viewed on the website in order to get popularity of it.')
    decimal_time = fields.Integer(
        'Decimal Time',
        help='This field shows the decimal time when a product is published'
        'on the website.')

    @api.cr_uid_ids_context
    def write(self, cr, uid, ids, values, context=None):
        for record in ids:
            if values.get('views', False):
                return super(WebsiteSeoMetadata, self).write(
                    cr, SUPERUSER_ID, [record], values)
            if values.get('website_published', False):
                now = datetime.now()
                decimal_time = time.mktime(now.timetuple())
                values['decimal_time'] = decimal_time
        return super(WebsiteSeoMetadata, self).write(
            cr, uid, ids, values)


class WebsiteProductMetadata(models.Model):
    _inherit = ["product.template", "website.seo.metadata"]
    _name = "product.template"

    public_categ_ids = fields.Many2many(
        "product.public.category",
        "product_public_category_product_template_rel",
        "product_template_id",
        "product_public_category_id")


class ProductPriceRanges(models.Model):
    _name = "product.price.ranges"

    lower = fields.Integer("Lower")
    upper = fields.Integer("Upper")


class ProductCategory(models.Model):
    _inherit = 'product.public.category'

    product_ids = fields.Many2many(
        "product.template", "product_public_category_product_template_rel",
        "product_public_category_id",
        "product_template_id", readonly=True)
    total_tree_products = fields.Integer("Total Subcategory Prods",
                                         compute="_get_product_count",
                                         store=False,)
    has_products_ok = fields.Boolean(compute="_get_has_products_ok",
                                     store=False, readonly=True)

    @api.depends("product_ids")
    @api.multi
    def _get_has_products_ok(self):
        for record in self:
            record.has_products_ok = self._child_has_products(record)

    def _child_has_products(self, category):
        if category.child_id:
            return any(self._child_has_products(child)
                       for child in category.child_id)
        elif category.product_ids.filtered(
                lambda r: r.website_published is True):
            return True
        else:
            return False

    @api.model
    def _get_async_ranges(self, category):
        prod_obj = self.env['product.template']
        ranges_obj = self.env['product.price.ranges'].search([])
        count_dict = {}
        prod_ids = []
        if category:
            prod_ids = prod_obj.search(
                [('public_categ_ids', 'child_of', int(category)),
                 ('website_published', '=', True)])
        if prod_ids:
            for prod in prod_ids:
                for ran in ranges_obj:
                    if ran.upper > prod.list_price > ran.lower:
                        if ran.id in count_dict.keys():
                            count_dict[ran.id] += 1
                        else:
                            count_dict[ran.id] = 1
                    if ran.id not in count_dict.keys():
                        count_dict[ran.id] = 0
            to_jsonfy = [{'id': k, 'qty': count_dict[k]} for k in count_dict]
            return to_jsonfy

    @api.model
    def _get_async_values(self, category):
        prod_obj = self.env['product.template']
        count_dict = {}
        prod_ids = []
        if category:
            prod_ids = prod_obj.search(
                [('public_categ_ids', 'child_of', int(category)),
                 ('website_published', '=', True)])
        if prod_ids:
            for prod in prod_ids:
                for line in prod.attribute_line_ids:
                    for value in line.value_ids:
                        if value.id in count_dict.keys():
                            count_dict[value.id] += 1
                        else:
                            count_dict[value.id] = 1
                        if value.id not in count_dict.keys():
                            count_dict[value.id] = 0
            to_jsonfy = [{'id': k, 'qty': count_dict[k]} for k in count_dict]
            return to_jsonfy

    @api.multi
    def _get_product_count(self):
        prod_obj = self.env["product.template"]
        for rec in self:
            prod_ids = prod_obj.search(
                [('public_categ_ids', 'child_of', rec.id),
                 ('website_published', '=', True)])
            rec.total_tree_products = len(prod_ids)
