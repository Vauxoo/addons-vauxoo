# coding: utf-8
import openerp
import datetime
from openerp.addons.web import http
from openerp.addons.web.http import request

MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = IMAGE_LIMITS = (1024, 768)
LOC_PER_PRODUCT_RSS = 45000
PRODUCT_RSS_CACHE_TIME = datetime.timedelta(minutes=1)


class WebsiteProductRSS(http.Controller):

    def create_product_rss(self, url, content):
        cr, uid, context = request.cr, openerp.SUPERUSER_ID, request.context
        ira = request.registry['ir.attachment']
        mimetype = 'application/xml;charset=utf-8'
        ira.create(cr, uid, dict(
            datas=content.encode('base64'),
            mimetype=mimetype,
            type='binary',
            name=url,
            url=url,
        ), context=context)

    @http.route('/product_rss.xml', type='http', auth="public", website=True)
    def rss_xml_index(self):
        cr, uid, context = request.cr, openerp.SUPERUSER_ID, request.context
        ira = request.registry['ir.attachment']
        user_obj = request.registry['res.users']
        user_brw = user_obj.browse(cr, uid, [uid], context=context)
        iuv = request.registry['ir.ui.view']
        product_obj = request.registry['product.template']
        mimetype = 'application/xml;charset=utf-8'
        content = None
        product_rss = ira.search_read(cr, uid, [
            ('name', '=', '/product_rss.xml'),
            ('type', '=', 'binary')],
            ('datas', 'create_date'), context=context)
        if product_rss:
            # Check if stored version is still valid
            server_format = openerp.tools.misc.DEFAULT_SERVER_DATETIME_FORMAT
            create_date = datetime.datetime.strptime(
                product_rss[0]['create_date'], server_format)
            delta = datetime.datetime.now() - create_date
            if delta < PRODUCT_RSS_CACHE_TIME:
                content = product_rss[0]['datas'].decode('base64')

        if not content:
            # Remove all RSS in ir.attachments as we're going to regenerate
            product_rss_ids = ira.search(cr, uid, [
                ('name', '=like', '/product_rss%.xml'),
                ('type', '=', 'binary')], context=context)
            if product_rss_ids:
                ira.unlink(cr, uid, product_rss_ids, context=context)

            pages = 0
            first_page = None
            values = {}
            product_ids = product_obj.search(cr, uid, [
                ('website_published', '=', True)])
            if product_ids:
                values['products'] = product_obj.browse(cr, uid, product_ids,
                                                        context)
            values['company'] = user_brw[0].company_id
            values['url_root'] = request.httprequest.url_root
            urls = iuv.render(cr, uid, 'website_product_rss.product_rss_locs',
                              values, context=context)
            if urls:
                page = iuv.render(cr, uid,
                                  'website_product_rss.product_rss_xml',
                                  dict(content=urls), context=context)
                if not first_page:
                    first_page = page
                pages += 1
                self.create_product_rss('/product_rss-%d.xml' % pages, page)
            if not pages:
                return request.not_found()
            elif pages == 1:
                content = first_page
        return request.make_response(content, [('Content-Type', mimetype)])
