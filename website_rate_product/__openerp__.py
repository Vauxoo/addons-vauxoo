# -*- encoding: utf-8 -*-
{
    "name": "Website Product Rate",
    "version": "1.0",
    "author": "Vauxoo",
    "category": "Website",
    "description": """
Website Product Rate
====================
    This app shows you a widget with five stars to give product ratings on the
    e-commerce platform.
    """,
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "website_sale"
    ],
    "demo": [],
    "data": [
        "views/layout.xml",
        "views/star_rate.xml",
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [
        "static/src/xml/rate.xml",
        "static/src/xml/mail.xml",
        ],
    "installable": True,
    "auto_install": False,
    "active": False
}
