# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'

    po_double_validation = fields.Selection(selection_add=[
        ('three_step', 'Get 3 levels of approvals to confirm a purchase order')
        ])

    po_third_validation_amount = fields.Monetary(
        string='Third validation amount', default=10000,
        help="Minimum amount for which a third validation is required")
