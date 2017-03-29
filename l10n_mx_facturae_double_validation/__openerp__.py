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
    'name': 'Double validation in account_invoice',
    'version': '1.0',
    'author': 'Vauxoo',
    'category': '',
    'depends': [
        'account',
    ],
    'demo': [],
    'website': 'https://www.vauxoo.com',
    'description': """
    This module performs twice Account invoice validation,
    performing the following.
    * Add a group "group_validator"
    * Hide the Validate button to the Draft invoice status
    * Add a button "By Validate" visible to all.
    * Add a state "By validating" to filter the invoices in the "By Validate"
      (Create the filter)
    * Add the button "validate" so that only users with the group
      "group_validator" can press it.
    * Users with the group "group_validator" will be able to validate
      the facura e.
    * Consider that states and buttons need to be done by workflow.

    """,
    'data': [
        'security/two_validations_security.xml',
        'views/two_validations_invoice_view.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'images': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
