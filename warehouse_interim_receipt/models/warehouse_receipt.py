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


class WarehouseReceipt(models.Model):

    _name = 'warehouse.receipt'
    _description = 'Warehouse Receipt'

    _rec_name = 'code'
    _order = 'sequence'

    sequence = fields.Integer(
        default=10,
        help='Sequence of the Warehouse receipt. Is an internal reference by'
             ' Odoo, it shouldn\'t be edit.')
    code = fields.Char(
        required=True,
        copy=False,
        help='Is the Warehouse receipt provide by the courier')

    @api.constrains('code')
    def check_unique_code(self):
        """
        The warehouse receipt code must be unique. If not raise a
        ValidationError
        """
        for whr in self:
            repeat_code = whr.search([('code', '=', whr.code),
                                      ('id', '!=', whr.id)])
            if repeat_code:
                raise ValidationError(
                    _('The warehouse receipt code must be unique'))
