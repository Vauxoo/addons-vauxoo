# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    'name': 'Portal CRM with Captcha',
    'version': '0.1',
    'category': 'Tools',
    'complexity': 'easy',
    'description': """
Contact page with Captcha widget.
=================================

You will need to install recaptcha and recaptcha client::

    $ sudo pip install recaptcha
    $ sudo pip install recaptcha-client

Added Menu 'Our Team ' as principal Menu, this menu show
the human recourses that is public.

    """,
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com',
    'depends': [
                'crm',
                'website_crm',
                'web_captcha',
                #~ 'portal_hr_employees', deprecated by odoo
                'vauxoo_widgets',
                ],
    'data': [
        'view/contact_view.xml',
    ],
    'test': [
        #'test/contact_form.yml',
    ],
    'installable': True,
    'auto_install': False,
    'css': [
    ],
    'js': [],
    'qweb': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
