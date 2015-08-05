# -*- encoding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: hugo@vauxoo.com
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################

{
    'name': 'Double validation in account_invoice',
    'version': '1.0',
    'author': 'Vauxoo',
    'category': '',
    'description': """
    Invoice Double Validation

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
    'depends': [
        'account',
    ],
    'demo': [],
    'website': 'https://www.vauxoo.com',
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
