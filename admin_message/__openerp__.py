# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Ma. Gabriela Quilarque (gabriela@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Administration Message",
    "version": "1.0",
    "author": "Vauxoo",
    "category": "Mail Message",
    "description": """
Administration for Messages
===========================

Module to added view replica of Mail Message,
localizate in: Settings->Technical -> Email ->Messages.

We create a new group "Admin Messages", this group will be able to edit and fix messages to have a
more clean content.

In this new view the technical information is hiden to avoid human mistakes.

This replica is to manage the look and feel correctly to administer, edit and improve messages
correctly.

With the correct namespace in form view, we avoid change the original behavior of the html widget
giving us more versatility to show the content.

If we install the module web_bootstrap3 on lp:~vauxoo/web-addons/7.0-web_hideleftmenu all styles
inside the html can be taken from bootstrap3[1]

The web_many2many_attachment dependency can be found here:

lp:~vauxoo/web-addons/7.0-web_hideleftmenu

[1] http://getbootstrap.com/
    """,
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    'depends': ['base',
                'base_setup',
                'web_many2many_attachments',
                'mail'], 
    "data": [
        "security/security_groups.xml",
        "view/mail_message_view.xml",
    ],
    "css": [
        "static/src/css/base.css",
        ],
    "installable": True,
    "active": False,
}
