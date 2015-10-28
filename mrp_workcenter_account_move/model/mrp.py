# coding: utf-8

from openerp import models, api


class MrpProduction(models.Model):
    """
    Production Orders / Manufacturing Orders
    """
    _inherit = 'mrp.production'
    _description = 'Manufacturing Order'

    @api.v7
    def _costs_generate(self, cr, uid, production):
        """ Calculates total costs at the end of the production.
        @param production: Id of production order.
        @return: Calculated amount.
        """
        return super(MrpProduction, self)._costs_generate(cr, uid, production)
