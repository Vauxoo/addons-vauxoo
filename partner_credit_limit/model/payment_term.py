
# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: hugo@vauxoo.com
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################
from openerp import models, fields


class PaymentTerm(models.Model):

    _inherit = 'account.payment.term'
    _order = 'sequence'

    sequence = fields.Integer(
        'Sequence', required=True,
        default=lambda self: self.env['ir.sequence'].get(
            'account.payment.term'))
