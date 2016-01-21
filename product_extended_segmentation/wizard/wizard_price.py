# -*- coding: utf-8 -*-
from openerp import fields, models


class WizardPrice(models.Model):
    _inherit = "wizard.price"

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

    update_avg_costs = fields.Boolean("Update Average Product Costs")