# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    std_price_neg_threshold = fields.Float(
        string="Standard Price Bottom Threshold (%)",
        help=('Maximum percentage threshold that Standard Price is '
              'allowed to lower')
    )

    @api.multi
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            {'std_price_neg_threshold':
             self.env.user.company_id.std_price_neg_threshold})
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env.user.company_id.std_price_neg_threshold = (
            self.std_price_neg_threshold)
