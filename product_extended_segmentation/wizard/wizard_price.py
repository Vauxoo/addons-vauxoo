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

    # /!\ NOTE: https://goo.gl/7wfpt1 Needs to use this approach
    def onchange_recursive(self, cr, uid, ids, recursive, context=None):
        template_id = context.get('active_id')
        res = self.pool.get('product.template').\
            compute_price(cr,  uid, product_ids=[],
                          template_ids=[template_id], test=True,
                          recursive=recursive, real_time_accounting=False,
                          context=context)

        res = str({template_id: sum([res[x] for x in res.keys()])})
        return {'value': {'info_field': res}}
