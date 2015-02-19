# -*- encoding: utf-8 -*-
{
    "name": "Website Comment Approval",
    "version": "1.0",
    "author": "Vauxoo",
    "category": "Website",
    "description": """
Website Comment Approval
========================
    This App lets the user approve comments on the products published on the
    website, it sets the value published to `False`.

    """,
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "website_sale",
    ],
    "demo": [],
    "data": [
        "views/layout.xml"
    ],
    "test": [],
    "qweb": [
        "static/src/xml/mail.xml",
             ],
    "installable": True,
    "auto_install": False,
    "active": False
}
