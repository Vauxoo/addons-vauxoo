{
    'name': 'Website Blog RSS',
    'category': 'website',
    'summary': 'This module enables RSS on Blog',
    'website': 'http://vauxoo.com',
    'version': '1.0',
    'description': """
        This App lets you create a RSS feed on populated by the
        blog posts stored on the database.
        """,
    'author': 'Vauxoo',
    'depends': [
        'website_blog',
    ],
    'data': [
        'views/website_templates.xml'

    ],
    'demo': [

    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
}
