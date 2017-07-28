# coding: utf-8
import datetime
from odoo import SUPERUSER_ID
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.web import http
from odoo.addons.web.http import request


MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = IMAGE_LIMITS = (1024, 768)
LOC_PER_BLOG_RSS = 45000
BLOG_RSS_CACHE_TIME = datetime.timedelta(minutes=1)


class WebsiteBlogRSS(http.Controller):

    def create_blog_rss(self, url, content):
        ira = request.env['ir.attachment'].sudo()
        mimetype = 'application/xml;charset=utf-8'
        ira.create(dict(
            datas=content.encode('base64'),
            mimetype=mimetype,
            type='binary',
            name=url,
            url=url,
        ))

    # TODO Rewrite this method to be generic and innheritable for any model
    @http.route('/blog_rss.xml', type='http', auth="public", website=True)
    def rss_xml_index(self):
        ira = request.env['ir.attachment']
        iuv = request.env['ir.ui.view']
        user_obj = request.env['res.users']
        blog_obj = request.env['blog.blog']
        config_obj = request.env['ir.config_parameter']

        blog_ids = blog_obj.sudo().search([])
        user_brw = user_obj.sudo().browse([SUPERUSER_ID])
        blog_post_obj = request.registry['blog.post']
        mimetype = 'application/xml;charset=utf-8'
        content = None
        blog_rss = ira.sudo().search_read([
            ('name', '=', '/blog_rss.xml'),
            ('type', '=', 'binary')],
            ('datas', 'create_date'))
        if blog_rss:
            # Check if stored version is still valid
            server_format =  DEFAULT_SERVER_DATETIME_FORMAT
            create_date = datetime.datetime.strptime(
                blog_rss[0]['create_date'], server_format)
            delta = datetime.datetime.now() - create_date
            if delta < BLOG_RSS_CACHE_TIME:
                content = blog_rss[0]['datas'].decode('base64')

        if not content:
            # Remove all RSS in ir.attachments as we're going to regenerate
            blog_rss_ids = ira.sudo().search([
                ('name', '=like', '/blog_rss%.xml'),
                ('type', '=', 'binary')])
            if blog_rss_ids:
                ira.sudo().unlink(blog_rss_ids)

            pages = 0
            first_page = None
            values = {}
            post_ids = blog_post_obj.sudo().search([
                ('website_published', '=', True)])
            if post_ids:
                values['posts'] = blog_post_obj.sudo().browse(post_ids)
            if blog_ids:
                blog = blog_obj.sudo().browse(blog_ids)[0]
                values['blog'] = blog
            values['company'] = user_brw[0].company_id
            values['website_url'] = config_obj.sudo().get_param('web.base.url')
            values['url_root'] = request.httprequest.url_root
            urls = iuv.sudo().render('website_blog_rss.blog_rss_locs', values)
            if urls:
                page = iuv.sudo().render(
                    'website_blog_rss.blog_rss_xml', dict(content=urls)
                )
                if not first_page:
                    first_page = page
                pages += 1
                self.create_blog_rss('/blog_rss-%d.xml' % pages, page)
            if not pages:
                return request.not_found()
            elif pages == 1:
                content = first_page
        return request.make_response(content, [('Content-Type', mimetype)])
