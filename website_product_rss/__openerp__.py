{
    'name': 'Website Product RSS',
    'category': 'website',
    'summary': 'This module enables RSS on Products',
    'website': 'http://vauxoo.com',
    'version': '1.0',
    'description': """
        This App lets you create a RSS feed on populated by the
        products stored on the database.
        """,
    'author': 'Vauxoo',
    'depends': [
        'website_sale',
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
