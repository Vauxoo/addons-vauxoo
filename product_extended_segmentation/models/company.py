# coding: utf-8

from odoo import _, api, models, fields
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    std_price_neg_threshold = fields.Float(
        string="Standard Price Bottom Threshold (%)",
        help='Maximum percentage threshold that Standard Price is allowed to'
        ' be lower in order to be changed with the update cost wizard',
        default=0.0)

    @api.constrains('std_price_neg_threshold')
    def _check_bottom_cost_threshold(self):
        if self.std_price_neg_threshold < 0:
            raise ValidationError(_('Bottom cost threshold must be positive'))
