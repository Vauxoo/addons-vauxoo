# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import api, fields


class ProductExtendedSegmentationSettings(osv.osv_memory):
    _inherit = 'purchase.config.settings'
    std_price_neg_threshold = fields.Float(
        string="Standard Price Bottom Threshold (%)",
        help=('Maximum percentage threshold that Standard Price is '
              'allowed to lower')
    )

    @api.model
    def default_get(self, fieldnames):
        res = super(ProductExtendedSegmentationSettings, self).\
            default_get(fieldnames)
        res['std_price_neg_threshold'] = \
            self.env.user.company_id.std_price_neg_threshold
        return res

    @api.multi
    def set_purchase_defaults(self):
        self.ensure_one()
        self.env.user.company_id.write({
            'std_price_neg_threshold': self.std_price_neg_threshold
        })
        return {}
