# coding: utf-8

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class MrpProduction(models.Model):
    """
    Production Orders / Manufacturing Orders
    """
    _inherit = 'mrp.production'
    _description = 'Manufacturing Order'

    @api.multi
    def test_production_done(self):
        self.ensure_one()
        if not self.routing_id:
            return super(MrpProduction, self).test_production_done()

        if not self.routing_id.journal_id:
            raise UserError(
                    _('Please set a Journal in Routing: {routing} to book '
                      'Production Cost Journal Entries'.format(
                          routing=self.routing_id.name)))
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
