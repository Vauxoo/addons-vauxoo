{
    "name": "Mail Channel Notify Tag",
    "summary": "Module to notify the channels when they are mentioned in the chatter",
    "author": "Vauxoo",
    "website": "https://www.vauxoo.com",
    "license": "LGPL-3",
    "category": "Productivity/Discuss",
    "version": "19.0.1.0.0",
    "depends": [
        "mail",
    ],
    "data": [
        "views/mail_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mail_channel_notify_tag/static/src/core/store_service_patch.js",
        ],
        "mail.assets_discuss_public": [
            "mail_channel_notify_tag/static/src/core/store_service_patch.js",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
}
