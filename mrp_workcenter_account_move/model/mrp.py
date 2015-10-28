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
    def test_accounting_setting(self):
        self.ensure_one()
        if not self.routing_id:
            return True

        # TODO: Check for analytical accounts. At company level set attribute
        analytical_account = True
        msg = ''
        msg_financial = _('Add Financial Account on Worcenter: {wc}\n')
        msg_hour = _('Add Hour Analytical Account on Worcenter: {wc}\n')
        msg_cycle = _('Add Cycle Analytical Account on Worcenter: {wc}\n')
        msg_journal = _('Please set a Journal in Routing: {routing} to book '
                        'Production Cost Journal Entries\n')

        if not self.routing_id.journal_id:
            msg += msg_journal.format(routing=self.routing_id.name)

        for line in self.workcenter_lines:
            wc = line.workcenter_id
            hour_cost = line.hour * wc.costs_hour
            cycle_cost = line.cycle * wc.costs_cycle

            if any([hour_cost, cycle_cost]):
                if not wc.costs_general_account_id:
                    msg += msg_financial.format(wc=wc.name)

            if not analytical_account:
                continue

            if hour_cost:
                if not wc.costs_hour_account_id:
                    msg += msg_hour.format(wc=wc.name)

            if cycle_cost:
                if not wc.costs_cycle_account_id:
                    msg += msg_cycle.format(wc=wc.name)
        if msg:
            raise UserError(msg)

        return super(MrpProduction, self).test_production_done()

    @api.multi
    def test_production_done(self):
        self.ensure_one()
        self.test_accounting_setting()
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
