# -*- coding: utf-8 -*-

from openerp import fields, models


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    print_name = fields.Char(size=50, translate=True)
