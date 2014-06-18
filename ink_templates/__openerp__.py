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
    'name' : 'Custom Templates',
    'version' : '0.1',
    'author' : 'Vauxoo',
    'category' : '',
    'description' : """

    Custom Templates
    ================
    - When you need to create a custom template with the email.template model
    and add some cool features to your template at the moment that you try to
    send it you see that the sanitize method of openerp changes all your
    template and became to a different template. To avoid this problem we
    created this module.

    How to Use
    ==========
    - In the template view we add 2 new fields in the Advanced page.  The first
    field is a boolean, used to define the template like important, this makes
    that template's content will be not sanitize.

    - The second field is a string, where you define the name of the attachment
    generated when you send your custom template, because the custom template
    will generate an attachment and puts it in the message post of the model
    """,
    'website': 'http://www.vauxoo.com',
    'images' : [],
    'depends' : [
        'mail',
        'email_template',
    ],
    'data': [
        'wizard/compose_mail_view.xml',
        'view/email_template_view.xml',
    ],
    'js': [
    ],
    'qweb' : [
    ],
    'css':[
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

