# coding: utf-8
{
    'name': 'Website Blog RSS',
    'category': 'website',
    'summary': 'This module enables RSS on Blog',
    'website': 'http://vauxoo.com',
    'version': '12.0.0.0.1',
    'author': 'Vauxoo, Tecnativa',
    'license': 'AGPL-3',
    'depends': [
        'website_blog',
    ],
    'data': [
        'data/update_blog_rss_cron.xml',
        'views/website_templates.xml',

    ],
    'demo': [

    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
}
