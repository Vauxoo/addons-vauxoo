# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: echeverrifm (echeverrifm@vauxoo.com)
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
    "name": "Stock hide set zero button",
    "version": "1.2",
    "author": "Vauxoo",
    "category": "",
    "description": """
When you are filling inventory then thios button can you make it make a 
mistake aftear load several lines.

Then:

This module add a group to not allow everybody with access to the document
make this kind of mitakes and add a message to confirm the action in order 
avoid human errors.

`See the image to know better which button we are talking about. <https://www.evernote.com/shard/s158/sh/1c691606-ad42-4019-b797-e78ad7701b65/555f3097424f995a64dad1d06950db51/deep/0/Inventory-Adjustments---Odoo.png>`_ 

    """,
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "base",
        "stock",
        ],
    "demo": [],
    "data": [
        "views/stock_view.xml",
        "security/stock_hide_set_zero_button.xml",
    ],
    "installable": True,
    "active": False,
}
