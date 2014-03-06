# -*- coding: utf-8 -*-
##############################################################################
#
#    Financed and Planified by Vauxoo
#    developed by: nhomar@vauxoo.com
#    developed by: luis@vauxoo.com
#    developed by: tulio@vauxoo.com
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
    'name': "Web Captcha",
    'author': "Vauxoo",
    'category': "Tools",
    'description': """
Some customizations for OpenERP web client made by Vauxoo

To use the Captcha Widget you should go to:

https://www.google.com/recaptcha

And generate a public and a private key.

You will need to go to the main company of your Openerp installation and
set the "Public Key" as the key for you.
    """,
    'version': "1.0",
    'depends': [
        'portal',
    ],
    'js': [
        'static/src/js/resource.js',
    ],
    'data': [
        'security/ir.model.access.csv',
        'view/company_view.xml',
        'view/res_captcha_view.xml',
        'view/ir_config_view.xml',
    ],
    'css': [

    ],
    'qweb': [
        'static/src/xml/template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'web_preload': False,
}
