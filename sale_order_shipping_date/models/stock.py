# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Jose Suniaga <josemiguel@vauxoo.com>
#    planned by: Gabriela Quilarte <gabriela@vauxoo.com>
############################################################################
from openerp import fields, models


class Orderpoint(models.Model):
    """ Defines Minimum stock rules. """
    _inherit = "stock.warehouse.orderpoint"

    # TODO: remove this in 0.0 migration
    # copied from Odoo 9.0 (commit 43e3663)
    lead_days = fields.Integer(
        'Lead Time', default=1,
        help="Number of days after the orderpoint is triggered to receive the"
        " products or to order to the vendor")
    lead_type = fields.Selection([
        ('net', 'Day(s) to get the products'),
        ('supplier', 'Day(s) to purchase')],
        string='Lead Type', required=True, default='supplier')
