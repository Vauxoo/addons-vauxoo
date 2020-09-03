from odoo import models, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.onchange('product_id', 'picking_type_id', 'company_id')
    def onchange_product_id(self):
        """Setting the responsible, this value was configured in the product
        previously"""

        res = super(MrpProduction, self).onchange_product_id()
        self.update(
            {'user_id': self.product_id.production_responsible.id})
        return res

    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.product_id:
            self.user_id = self.product_id.production_responsible.id
