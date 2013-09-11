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
    
        Module to added view replica of Mail Message,
        localizate in: Settings->Technical -> Email ->Messages.
        
        Added attribute class=bs3 in form of view.
    """,
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    'depends': ['base', 'base_setup','mail'], 
    "data": [
        "security/security_groups.xml",
        "view/mail_message_view.xml",
    ],
    "installable": True,
    "active": False,
}
