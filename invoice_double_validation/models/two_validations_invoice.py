# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: hugo@vauxoo.com
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################

from openerp import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    state = fields.Selection(
        selection_add=[('validate', 'By validating')],
        help=' * The \'Draft\' status is used when a user is \
            encoding a new and unconfirmed Invoice. \
            \n* The \'By validating\' status is used when an invoice is \
            ready to be validate. \
            \n* The \'Pro-forma\' when invoice is in Pro-forma \
            status,invoice does not have an invoice number. \
            \n* The \'Open\' status is used when user create invoice,\
            a invoice number is generated.Its in open status till user \
            does not pay invoice. \
            \n* The \'Paid\' status is set automatically when the invoice \
            is paid. Its related journal entries may or may not be reconciled.\
            \n* The \'Cancelled\' status is used when user cancel invoice.')
