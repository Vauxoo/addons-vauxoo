from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom,
                         location_id, name, origin, values, bom):
        """When the MO is created from a procurement rule the responsible of
        the product is set in the new MO created"""
        res = super(StockRule, self)._prepare_mo_vals(
            product_id, product_qty, product_uom, location_id, name, origin,
            values, bom)
        res.update(
            {'user_id': product_id.production_responsible.id}
        )
        return res
