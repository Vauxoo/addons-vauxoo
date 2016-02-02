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
from datetime import date, timedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _get_date_due(self):
        date_due = date.today()
        days_conf = self.env['ir.config_parameter'].search(
            [('key', '=', 'sale.days_due_date')])
        if days_conf:
            date_due = date_due + timedelta(days=int(days_conf.value) or 0.0)
        return date_due.strftime('%Y-%m-%d')

    date_due = fields.Date(
        'Date Due', default=_get_date_due,
        help='Date due to finish this sale order, the value is calculated '
        'with the today date + days configured in Settings/Sales')
