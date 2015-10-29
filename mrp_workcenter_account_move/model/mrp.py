# coding: utf-8

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class MrpProduction(models.Model):
    """
    Production Orders / Manufacturing Orders
    """
    _inherit = 'mrp.production'
    _description = 'Manufacturing Order'
    account_move_id = fields.Many2one(
        'account.move',
        string='Cost Journal Entry',
        readonly=True,
        )

    @api.multi
    def test_accounting_setting(self):
        self.ensure_one()
        if not self.routing_id:
            return True

        company_brw = self.env.user.company_id
        require_workcenter_analytic = company_brw.require_workcenter_analytic

        msg = ''
        msg_financial = _('Add Financial Account on Worcenter: {wc}\n')
        msg_hour = _('Add Hour Analytical Account on Worcenter: {wc}\n')
        msg_cycle = _('Add Cycle Analytical Account on Worcenter: {wc}\n')
        msg_journal = _('Please set a Journal in Routing: {routing} to book '
                        'Production Cost Journal Entries\n')
        msg_location = _('Add Financial Account on Location: {location}\n')

        if not self.product_id.property_stock_production.\
                valuation_in_account_id:
            msg += msg_location.format(
                location=self.product_id.property_stock_production.name)

        if not self.routing_id.journal_id:
            msg += msg_journal.format(routing=self.routing_id.name)

        for line in self.workcenter_lines:
            wc = line.workcenter_id
            hour_cost = line.hour * wc.costs_hour
            cycle_cost = line.cycle * wc.costs_cycle

            if any([hour_cost, cycle_cost]):
                if not wc.costs_general_account_id:
                    msg += msg_financial.format(wc=wc.name)

            if not require_workcenter_analytic:
                continue

            if hour_cost:
                if not wc.costs_hour_account_id:
                    msg += msg_hour.format(wc=wc.name)

            if cycle_cost:
                if not wc.costs_cycle_account_id:
                    msg += msg_cycle.format(wc=wc.name)
        if msg:
            raise UserError(msg)

        return True

    @api.multi
    def test_production_done(self):
        self.ensure_one()
        self.test_accounting_setting()
        return super(MrpProduction, self).test_production_done()

    @api.multi
    def check_create_accounting_entry(self):
        self.ensure_one()
        amount = 0.0
        for wc_line in self.workcenter_lines:
            wc = wc_line.workcenter_id
            if wc.costs_journal_id and wc.costs_general_account_id:
                # Cost per hour
                amount += wc_line.hour * wc.costs_hour
                # Cost per cycle
                amount += wc_line.cycle * wc.costs_cycle
        return amount

    @api.multi
    def _create_account_move(self):
        self.ensure_one()
        ctx = dict(self._context)
        ap_obj = self.env['account.period']
        am_obj = self.env['account.move']
        date = fields.Date.context_today(self)
        vals = {
            'journal_id': self.routing_id.journal_id.id,
            'period_id': ap_obj.with_context(ctx).find(date)[:1].id,
            'date': date,
            'ref': self.name,
            'company_id': self.company_id.id,
        }
        return am_obj.with_context(ctx).create(vals)

    @api.multi
    def _create_account_move_line(self, move_id, production_account_id):
        """
        Generate the account.move.line values to track the production cost.
        """
        self.ensure_one()
        aml_obj = self.env['account.move.line']

        for line in self.workcenter_lines:
            wc = line.workcenter_id
            hour_cost = line.hour * wc.costs_hour
            cycle_cost = line.cycle * wc.costs_cycle

            if not any([hour_cost, cycle_cost]):
                continue

            base_line = dict(
                move_id=move_id.id,
                product_id=wc.product_id.id,
                product_uom_id=wc.product_id and wc.product_id.uom_id.id,)

            if cycle_cost:
                base_cycle = dict(
                    base_line,
                    name=line.name + ' (C)',
                    quantity=line.cycle,)
                debit_cycle = dict(
                    base_cycle,
                    debit=cycle_cost,
                    account_id=production_account_id,)
                credit_cycle = dict(
                    base_cycle,
                    credit=cycle_cost,
                    account_id=wc.costs_general_account_id.id,
                    analytic_account_i= wc.costs_cycle_account_id.id,
                    )
                aml_obj.create(debit_cycle)
                aml_obj.create(credit_cycle)

            if hour_cost:
                base_hour = dict(
                    base_line,
                    name=line.name + ' (H)',
                    quantity=line.hour,)
                debit_hour = dict(
                    base_hour,
                    debit=hour_cost,
                    account_id=production_account_id,
                    )
                credit_hour = dict(
                    base_hour,
                    credit=hour_cost,
                    account_id=wc.costs_general_account_id.id,
                    analytic_account_i= wc.costs_hour_account_id.id,
                    )
                aml_obj.create(debit_hour)
                aml_obj.create(credit_hour)
        return True

    @api.multi
    def _create_accounting_entries(self, move_id):
        self.ensure_one()
        production_account_id = self.product_id.property_stock_production.\
            valuation_in_account_id.id
        return self._create_account_move_line(move_id, production_account_id)

    @api.v7
    def _costs_generate(self, cr, uid, production):
        """ Calculates total costs at the end of the production.
        @param production: Id of production order.
        @return: Calculated amount.
        """
        amount = self.check_create_accounting_entry(cr, uid, production.id)
        if not amount:
            return amount

        move_id = self._create_account_move(cr, uid, production.id)
        production.write({'account_move_id': move_id.id})
        self._create_accounting_entries(cr, uid, production.id, move_id)

        return amount


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
