# -*- coding: utf-8 -*-
# Copyright 2017 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    margin_threshold = fields.Float(default=0, digits=(16, 2))
