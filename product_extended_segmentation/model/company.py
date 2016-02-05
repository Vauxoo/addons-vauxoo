# coding: utf-8

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    std_price_neg_threshold = fields.Float(
        string="Standard Price Negative Threshold (%)",
        help=('Maximum percentage threshold that Standard Price is '
              'allowed to lower'))
