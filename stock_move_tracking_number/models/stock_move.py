# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Katherine Zaoral <kathy@vauxoo.com>
#    planned by: Rafael Silva <rsilvam@vauxoo.com>
############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class StockMove(models.Model):

    _inherit = 'stock.move'

    tracking_number = fields.Text(
        states={'done': [('readonly', True)]},
        help='Tracking Number added by the user to organize the incoming'
             ' products. This field can only be modify in the move is not'
             ' in done state')

    @api.constrains('tracking_number')
    def check_modify_trcking_number(self):
        if self.state == 'done':
            raise ValidationError(_(
                'The tracking number can not be modify in a done move'))
