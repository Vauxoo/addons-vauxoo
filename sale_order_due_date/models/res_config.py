# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2016 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Luis Torres <luis_t@vauxoo.com>
############################################################################
from openerp import models, fields, api


class SaleConfigSettings(models.Model):
    _inherit = 'sale.config.settings'

    days_due_date_sale = fields.Integer(
        'Days to due date',
        help='Number of days that will add to the date when is created the '
        'sale order as due date.')

    @api.multi
    def set_days_due_date(self):
        param = self.env['ir.config_parameter'].search(
            [('key', '=', 'sale.days_due_date')])
        if param:
            param.write({'value': self.days_due_date_sale})
        return True

    @api.multi
    def get_default_days_due_date_sale(self):
        days = self.env['ir.config_parameter'].search(
            [('key', '=', 'sale.days_due_date')])
        return {'days_due_date_sale': int(days.value) or 0.0}
