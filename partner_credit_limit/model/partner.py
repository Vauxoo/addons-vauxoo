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
from openerp import models, fields


class res_partner(models.Model):
    _inherit = 'res.partner'

    over_credit = fields.Boolean('Allow Over Credit?', required=False)
    maturity_over_credit = fields.Boolean(
        'Allow Maturity Over Credit?', required=False)
    credit_maturity_limit = fields.Float(string='Credit Maturity Limit')
    grace_payment_days = fields.Float(
        'Days grace payment',
        help='Days grace payment')
