# -*- encoding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from tools.translate import _

class account_asset_asset(osv.osv):
    _inherit = 'account.asset.asset'

    def onchange_category_id(self, cr, uid, ids, category_id, context=None):
        context = context or {}
        val = super(account_asset_asset, self).onchange_category_id(cr, uid, ids, category_id, context=context)
        val = val or {'value':{}}
        if category_id:
            category = self.pool.get('account.asset.category').browse(cr, uid, category_id, context=context)
            if category.account_analytic_id:
                val['value']['account_analytic_id'] = category.account_analytic_id.id
        return val

    _columns = {
        'account_analytic_id': fields.many2one('account.analytic.account', 'Analytic account'),
    }

