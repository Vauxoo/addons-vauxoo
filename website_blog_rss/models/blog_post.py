import time
import datetime
import base64
from email import utils
from odoo import models, fields, api
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class BlogPost(models.Model):
    _inherit = 'blog.post'

    @api.multi
    def _compute_get_date(self):
        posts = self
        for post in posts:
            write_tuple = post.write_date.date().timetuple()
            timestamp = time.mktime(write_tuple)
            post.date_rfc2822 = utils.formatdate(timestamp)

    date_rfc2822 = fields.Char(compute='_compute_get_date')

    @api.model
    def _get_previous_blog_rss(self):
        cache_time = self.env['ir.config_parameter'].sudo().get_param(
            'blog.rss.cache.time')
        blog_cache = datetime.datetime.now() - datetime.timedelta(
            minutes=int(cache_time))
        worging_date = blog_cache.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        blog_rss = self.env['ir.attachment'].search([
            ('name', 'ilike', '/blog_rss%.xml'),
            ('type', '=', 'binary'),
            ('create_date', '>=', worging_date)], limit=1)
        return blog_rss and base64.b64decode(blog_rss.datas)

    @api.model
    def _get_blog_rss_content(self, blog=None):
        """Return Blog rss content build it from all blog post"""
        view = self.env['ir.ui.view']
        blog_obj = self.env['blog.blog']
        blog_post = self.env['blog.post']
        blog_ids = blog.ids if blog else blog_obj.search([], limit=1).ids
        values = {}
        post_domain = [('website_published', '=', True)]
        if blog_ids:
            post_domain += [("blog_id", "in", blog_ids)]
            values['blog'] = blog_obj.browse(blog_ids)
        values['posts'] = blog_post.search(post_domain)
        values['company'] = self.env.user.company_id
        values['website_url'] = self.env[
            'ir.config_parameter'].get_param('web.base.url')
        values['url_root'] = '%s/' % values['website_url']
        return view.render_template('website_blog_rss.blog_rss_xml', values)

    @api.model
    def _update_blog_rss(self):
        content = self._get_previous_blog_rss()
        att = self.env['ir.attachment'].search(
            [('name', '=like', '/blog_rss%.xml'), ('type', '=', 'binary')])
        att.unlink()
        content = self._get_blog_rss_content()
        att.create(dict(
            datas=base64.b64encode(content),
            mimetype='application/xml;charset=utf-8', type='binary',
            name='/blog_rss.xml', url='/blog_rss.xml',
            public=True))
        return True
