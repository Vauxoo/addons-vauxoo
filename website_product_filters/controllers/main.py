# -*- coding: utf-8 -*-
import werkzeug
import openerp
from openerp import SUPERUSER_ID
from openerp import http
from openerp import tools
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website_sale.controllers.main import QueryURL


class WebsiteSale(website_sale):
    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'  # noqa
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        """
        This method was inherited wit the purpose of filtering attributes
        instead of showing all that exist on the instance, it will allow
        to show attribute filters based on the selected category.
        """
        cr, uid, context, pool = (request.cr,
                                  request.uid,
                                  request.context,
                                  request.registry)
        res = super(WebsiteSale, self).shop(page=page,
                                            category=category,
                                            search=search, ppg=ppg,
                                            **post)
        attributes_obj = pool['product.attribute']
        attribute_ids = self._get_used_attrs(category)
        attributes = attributes_obj.browse(cr, uid, attribute_ids,
                                           context=context)
        res.qcontext['attributes'] = attributes
        args = res.qcontext['keep'].args
        for arg in args.get('attrib', []):
            attr_id = arg.split('-')
            if int(attr_id[0]) not in attribute_ids:
                res.qcontext['keep'] = QueryURL(
                    '/shop',
                    category=category and int(category),
                    search=search)
        return res

    def _get_used_attrs(self, category):
        """
        This method retrieves all ids of the category selected on the
        website.
        """
        cr, uid, context, pool = (request.cr,
                                  request.uid,
                                  request.context,
                                  request.registry)
        attribute_ids = []
        attributes = []
        prod_ids = []
        product_obj = pool['product.template']
        if category:
            prod_ids = product_obj.search(
                cr,
                uid,
                [('public_categ_ids', '=', category.id)], context=context)
            for product in product_obj.browse(cr, uid, prod_ids, context=context):
                for attribute in product.attribute_line_ids:
                    if attribute.attribute_id.id not in attribute_ids:
                        attribute_ids.append(attribute.attribute_id.id)

        return attribute_ids

openerp.addons.website_sale.controllers.main.website_sale = WebsiteSale
