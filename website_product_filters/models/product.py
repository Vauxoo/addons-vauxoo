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
from datetime import datetime
import time
from openerp import models, fields, api
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

    _parent_store = True
    _order = 'parent_left'

    parent_left = fields.Integer('Left Parent', select=1)
    parent_right = fields.Integer('Right Parent', select=1)
    parent_id = fields.Many2one(ondelete='restrict')

    product_ids = fields.Many2many(
        "product.template", "product_public_category_product_template_rel",
        "product_public_category_id",
        "product_template_id", readonly=True)
    total_tree_products = fields.Integer("Total Subcategory Prods",
                                         compute="_get_product_count",
                                         store=True)
    has_products_ok = fields.Boolean(compute="_get_product_count",
                                     store=True, readonly=True)

    @api.model
    def _get_async_ranges(self, category):
        prod_obj = self.env['product.product']
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
                    if ran.upper > prod.lst_price > ran.lower:
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
        prod_obj = self.env['product.product']
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

    @api.depends("product_ids", "product_ids.website_published")
    def _get_product_count(self):
        prod_obj = self.env["product.product"]
        for rec in self:
            prod_ids = prod_obj.search(
                [('public_categ_ids', 'child_of', rec.id),
                 ('website_published', '=', True)])
            rec.total_tree_products = len(prod_ids)
            rec.has_products_ok = True and len(prod_ids) > 0 or False
