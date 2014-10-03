# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Financed and Planified by Vauxoo
#    developed by: nhomar@vauxoo.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "Customize OpenERP web client",
    'author': "Vauxoo",
    'category': "Web",
    'description': """
    Some customizations for OpenERP web client made by Vauxoo
    """,
    'version': "1.0",
    'depends': ['web',
    ],
    'js': [
    ],
    'css': [
        'static/src/css/style.css',
    ],
    'qweb': [
        'static/src/xml/web_vauxoo_cust.xml',
    ],
    'installable': True,
    'auto_install': False,
    'web_preload': False,
}
