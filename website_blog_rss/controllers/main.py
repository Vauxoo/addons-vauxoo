# coding: utf-8
from odoo import http
from odoo.http import request


class WebsiteBlogRSS(http.Controller):

    @http.route(['/blog_rss.xml', "/blog/<model('blog.blog'):blog>/rss.xml"],
                type='http', auth="public", website=True)
    def rss_xml_index(self, blog=False):
        """Controller that retrive all the blog post"""
        blog_obj = request.env['blog.post']
        content = blog_obj._get_previous_blog_rss()
        if not content:
            return request.not_found()
        return request.make_response(
            content, [('Content-Type', 'application/xml;charset=utf-8')])
