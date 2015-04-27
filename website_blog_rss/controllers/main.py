# -*- coding: utf-8 -*-
import openerp
import datetime
from openerp.addons.web import http
from openerp.addons.web.http import request

MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = IMAGE_LIMITS = (1024, 768)
LOC_PER_BLOG_RSS = 45000
BLOG_RSS_CACHE_TIME = datetime.timedelta(minutes=1)


class WebsiteBlogRSS(http.Controller):

    def create_blog_rss(self, url, content):
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

    @http.route('/blog_rss.xml', type='http', auth="public", website=True)
    def rss_xml_index(self):
        cr, uid, context = request.cr, openerp.SUPERUSER_ID, request.context
        ira = request.registry['ir.attachment']
        iuv = request.registry['ir.ui.view']
        blog_post_obj = request.registry['blog.post']
        mimetype = 'application/xml;charset=utf-8'
        content = None
        blog_rss = ira.search_read(cr, uid, [
            ('name', '=', '/blog_rss.xml'),
            ('type', '=', 'binary')],
            ('datas', 'create_date'), context=context)
        if blog_rss:
            # Check if stored version is still valid
            server_format = openerp.tools.misc.DEFAULT_SERVER_DATETIME_FORMAT
            create_date = datetime.datetime.strptime(
                blog_rss[0]['create_date'], server_format)
            delta = datetime.datetime.now() - create_date
            if delta < BLOG_RSS_CACHE_TIME:
                content = blog_rss[0]['datas'].decode('base64')

        if not content:
            # Remove all RSS in ir.attachments as we're going to regenerate
            blog_rss_ids = ira.search(cr, uid, [
                ('name', '=like', '/blog_rss%.xml'),
                ('type', '=', 'binary')], context=context)
            if blog_rss_ids:
                ira.unlink(cr, uid, blog_rss_ids, context=context)

            pages = 0
            first_page = None
            values = {}
            post_ids = blog_post_obj.search(cr, uid, [
                ('website_published', '=', True)])
            if post_ids:
                values['posts'] = blog_post_obj.browse(cr, uid, post_ids,
                                                       context)
            values['url_root'] = request.httprequest.url_root
            urls = iuv.render(cr, uid, 'website_blog_rss.blog_rss_locs',
                              values, context=context)
            if urls:
                page = iuv.render(cr, uid, 'website_blog_rss.blog_rss_xml',
                                  dict(content=urls), context=context)
                if not first_page:
                    first_page = page
                pages += 1
                self.create_blog_rss('/blog_rss-%d.xml' % pages, page)
            if not pages:
                return request.not_found()
            elif pages == 1:
                content = first_page
        return request.make_response(content, [('Content-Type', mimetype)])
