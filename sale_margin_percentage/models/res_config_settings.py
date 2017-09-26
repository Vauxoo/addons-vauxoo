# -*- coding: utf-8 -*-
# Copyright 2017 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'

    margin_threshold = fields.Float(
        related='company_id.margin_threshold',
        help="Margin Threshold for product in order lines")
