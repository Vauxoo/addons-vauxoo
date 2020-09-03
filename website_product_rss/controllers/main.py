import base64
import odoo
import datetime
from odoo import http
from odoo.http import request

MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = IMAGE_LIMITS = (1024, 768)
LOC_PER_PRODUCT_RSS = 45000
PRODUCT_RSS_CACHE_TIME = datetime.timedelta(minutes=1)


class WebsiteProductRSS(http.Controller):

    def create_product_rss(self, url, content):
        ira = request.env['ir.attachment']
        mimetype = 'application/xml;charset=utf-8'
        ira.create(dict(
            datas=base64.b64encode(content),
            mimetype=mimetype,
            type='binary',
            name=url,
            url=url,
        ))

    @http.route('/product_rss.xml', type='http', auth="public", website=True)
    def rss_xml_index(self):
        uid = odoo.SUPERUSER_ID
        ira = request.env['ir.attachment'].sudo()
        user_obj = request.env['res.users']
        user_brw = user_obj.browse([uid])
        iuv = request.env['ir.ui.view']
        product_obj = request.env['product.template']
        mimetype = 'application/xml;charset=utf-8'
        content = None
        product_rss = ira.search_read([
            ('name', '=', '/product_rss.xml'),
            ('type', '=', 'binary')],
            ('datas', 'create_date'))
        if product_rss:
            # Check if stored version is still valid
            server_format = odoo.tools.misc.DEFAULT_SERVER_DATETIME_FORMAT
            create_date = datetime.datetime.strptime(
                product_rss[0]['create_date'], server_format)
            delta = datetime.datetime.now() - create_date
            if delta < PRODUCT_RSS_CACHE_TIME:
                content = base64.b64decode(product_rss[0]['datas'])

        if not content:
            # Remove all RSS in ir.attachments as we're going to regenerate
            product_rss_ids = ira.search([
                ('name', '=like', '/product_rss%.xml'),
                ('type', '=', 'binary')])
            if product_rss_ids:
                product_rss_ids.unlink()

            pages = 0
            first_page = None
            values = {}
            product_ids = product_obj.search([
                ('website_published', '=', True)])
            if product_ids:
                values['products'] = product_ids
            values['company'] = user_brw[0].company_id
            values['url_root'] = request.httprequest.url_root
            urls = iuv.render_template('website_product_rss.product_rss_locs',
                                       values)
            if urls:
                page = iuv.render_template(
                    'website_product_rss.product_rss_xml', dict(content=urls))
                if not first_page:
                    first_page = page
                pages += 1
                self.create_product_rss('/product_rss-%d.xml' % pages, page)
            if not pages:
                return request.not_found()
            if pages == 1:
                content = first_page
        return request.make_response(content, [('Content-Type', mimetype)])
