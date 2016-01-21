# -*- coding: utf-8 -*-
from openerp import fields, models


class WizardPrice(models.Model):
    _inherit = "wizard.price"

    update_avg_costs = fields.Boolean("Update Average Product Costs")

    def compute_from_bom(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context.update({
            'update_avg_costs': self.browse(cr, uid, ids).update_avg_costs
        })

        res = super(WizardPrice, self).compute_from_bom(cr, uid, ids, context)

    def onchange_recursive(self, cr, uid, ids, recursive, context=None):
        product_tmpl = self.pool.get('product.template')
        active_id = context.get('active_id')
        res = {}
        if context.get('active_model') == 'product.template':
            res = product_tmpl.compute_price(
                cr, uid, [], template_ids=[active_id], test=True,
                recursive=recursive, real_time_accounting=False,
                context=context)
        else:
            res = product_tmpl.compute_price(
                cr, uid, product_ids=[active_id], template_ids=[], test=True,
                recursive=recursive, real_time_accounting=False,
                context=context)

        res = str({active_id: sum([res[x] for x in res.keys()])})
        return {'value': {'info_field': res}}
