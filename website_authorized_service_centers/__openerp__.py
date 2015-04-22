{
    'name': 'Autorized Service Centers',
    'category': 'Website',
    'summary': 'Show your trusted service centers',
    'website': 'https://www.vauxoo.com/',
    'version': '1.0',
    'description': """
Autorized Service Centers
=========================
    This App lets you create some Brands on the backend
    and associate the given brands to partners marked as
    service providers to be displayed on the 'Authorized
    Service Centers' page.

    + For in order to install this module download this repo
        - https://github.com/JayVora-SerpentCS/SerpentCS_Contributions-v8.git
    and install the `website_product_brand` module.

        """,
    'author': 'Vauxoo',
    'depends': [
        'website_product_brand',
    ],
    'data': [
        'views/layout.xml',
        'views/product_brand_view.xml',
        'views/authorized_service_centers.xml',
    ],
    'demo': [

    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
}
