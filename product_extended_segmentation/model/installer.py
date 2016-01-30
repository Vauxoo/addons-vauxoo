# -*- coding: utf-8 -*-
from openerp.osv import fields, osv


class ProductExtendedSegmentationSettings(osv.osv_memory):
    _inherit = 'purchase.config.settings'
    _columns = {
        'std_price_neg_threshold': fields.float(
            string="Standard Price Negative Threshold (%)",
            help=('Maximum percentage threshold that Standard Price is '
                  'allowed to lower')),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(
            ProductExtendedSegmentationSettings, self).default_get(
                cr, uid, fields, context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        res['std_price_neg_threshold'] =\
            user.company_id.std_price_neg_threshold
        return res

    _defaults = {
        'std_price_neg_threshold': 1.0,
    }

    def set_purchase_defaults(self, cr, uid, ids, context=None):
        # super(
        #     ProductExtendedSegmentationSettings, self).set_purchase_defaults(
        #         cr, uid, context)
        wizard = self.browse(cr, uid, ids)[0]
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        user.company_id.write(
            {'std_price_neg_threshold': wizard.std_price_neg_threshold})
        return {}
