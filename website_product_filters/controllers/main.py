# coding: utf-8
import openerp
from openerp import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website_sale.controllers.main import QueryURL


class WebsiteSale(website_sale):

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>',  # noqa
        '/shop/brands'], type='http', auth="public", website=True)
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
        ranges_obj = pool['product.price.ranges']
        brand_obj = pool['product.brand']
        template_obj = pool['product.template']
        ranges_list = request.httprequest.args.getlist('range')
        brand_list = request.httprequest.args.getlist('brand')
        brand_selected_ids = [int(b) for b in brand_list if b]
        ranges_selected_ids = [int(v) for v in ranges_list if v]
        ranges_selected = ranges_obj.browse(cr, uid, ranges_selected_ids,
                                            context=context)
        filtered_products = res.qcontext['products']
        range_product_ids = []
        for rang in ranges_selected:
            for fproduct in filtered_products:
                if rang.lower <= fproduct.lst_price <= rang.upper:
                    range_product_ids.append(fproduct.id)
        if range_product_ids:
            new_products = template_obj.browse(
                cr,
                uid,
                range_product_ids,
                context=context)
        else:
            new_products = filtered_products
        ranges_ids = ranges_obj.search(cr, uid, [], context=context)
        ranges = ranges_obj.browse(cr, uid, ranges_ids, context=context)
        attribute_ids = self._get_used_attrs(category)
        brand_ids = self._get_category_brands(category)
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
        brands = brand_obj.browse(cr, uid, brand_ids, context=context)

        parent_category_ids = []
        if category:
            parent_category_ids = [category.id]
            current_category = category
            while current_category.parent_id:
                parent_category_ids.append(current_category.parent_id.id)
                current_category = current_category.parent_id
        category_obj = pool['product.public.category']
        category_ids = category_obj.search(
            cr, uid, [('parent_id', '=', False)], context=context)
        categs = category_obj.browse(cr, uid, category_ids, context=context)

        res.qcontext['parent_category_ids'] = parent_category_ids
        res.qcontext['brands'] = brands
        res.qcontext['categories'] = categs
        res.qcontext['products'] = new_products
        res.qcontext['price_ranges'] = ranges
        res.qcontext['brand_set'] = brand_selected_ids
        res.qcontext['ranges_set'] = ranges_selected_ids
        return res

    def _normalize_category(self, category):
        """
        This method returns a condition value usable on tuples, because
        sometimes category can come from different places, sometimes it
        can be an Odoo object and some others an int or a unicode.
        """
        if isinstance(category, int) or isinstance(category, unicode):
            cond = int(category)
        else:
            cond = category.id
        return cond

    def _get_category_brands(self, category):
        cr, uid, context, pool = (request.cr,
                                  request.uid,
                                  request.context,
                                  request.registry)
        prod_ids = []
        brand_ids = []
        product_obj = pool['product.template']
        if category:
            cond = self._normalize_category(category)
            prod_ids = product_obj.search(cr, uid,
                                          [('public_categ_ids', '=', cond)],
                                          context=context)
            for prod in product_obj.browse(cr, uid, prod_ids, context=context):
                if prod.product_brand_id.id not in brand_ids and prod.product_brand_id.id:  # noqa
                    brand_ids.append(prod.product_brand_id.id)
        return brand_ids

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
        prod_ids = []
        product_obj = pool['product.template']
        if category:
            cond = self._normalize_category(category)
            prod_ids = product_obj.search(
                cr,
                uid,
                [('public_categ_ids', '=', cond)], context=context)
            for product in product_obj.browse(cr, uid, prod_ids,
                                              context=context):
                for attribute in product.attribute_line_ids:
                    if attribute.attribute_id.id not in attribute_ids:
                        attribute_ids.append(attribute.attribute_id.id)

        return attribute_ids

    @http.route(['/shop/product/<model("product.template"):product>'],
                type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        cr, uid, context, pool =\
            request.cr, request.uid, request.context, request.registry
        template_obj = pool['product.template']
        viewed = product.views + 1
        template_obj.write(cr, uid, [product.id],
                           {'views': viewed}, context=context)
        res = super(WebsiteSale, self).product(product=product,
                                               category=category,
                                               search=search, **kwargs)
        return res

openerp.addons.website_sale.controllers.main.website_sale = WebsiteSale
