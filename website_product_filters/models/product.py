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


class ProductPriceRanges(models.Model):
    _name = "product.price.ranges"

    lower = fields.Integer("Lower")
    upper = fields.Integer("Upper")


class ProductCategory(models.Model):
    _inherit = 'product.public.category'

    @api.multi
    def _get_products(self):
        product_obj = self.env["product.template"]
        for record in self:
            product_ids = []
            product_published = product_obj.search(
                [("website_published", "=", True)])

            for product in product_published:
                if record in product.public_categ_ids:
                    product_ids.append(product.id)
            record.product_ids = product_ids

    product_ids = fields.Many2many('product.template', compute="_get_products")
    total_tree_products = fields.Integer("Total Subcategory Prods",
                                         compute="_get_product_count",
                                         store=True,)

    @api.multi
    @api.depends('product_ids')
    def _get_product_count(self):
        prod_obj = self.env["product.template"]
        for rec in self:
            prod_ids = prod_obj.search(
                [('public_categ_ids', 'child_of', rec.id),
                 ('website_published', '=', True)])
            rec.total_tree_products = len(prod_ids)
