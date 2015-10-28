# coding: utf-8

from openerp import models, fields, api


class MrpProduction(models.Model):
    """
    Production Orders / Manufacturing Orders
    """
    _inherit = 'mrp.production'
    _description = 'Manufacturing Order'

    @api.multi
    def test_production_done(self):
        # TODO: make a check on costs_general_account_id in workcenter_lines as
        # this will become mandatory by using this module and journal_id in
        # routings as it will be used to create Journal Entries
        self.ensure_one()
        return super(MrpProduction, self).test_production_done()

    @api.v7
    def _costs_generate(self, cr, uid, production):
        """ Calculates total costs at the end of the production.
        @param production: Id of production order.
        @return: Calculated amount.
        """
        return super(MrpProduction, self)._costs_generate(cr, uid, production)


class MrpRouting(models.Model):
    """
    For specifying the routings of Work Centers.
    """
    _inherit = 'mrp.routing'
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        readonly=False,
        )
