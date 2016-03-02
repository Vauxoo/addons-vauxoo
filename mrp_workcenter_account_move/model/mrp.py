# coding: utf-8

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning as UserError


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
        copy=False,
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
        msg_location = _('Add Financial Account on Location: {location} '
                         'For product: {product}\n')

        if not self.product_id.property_stock_production.\
                valuation_in_account_id:
            msg += msg_location.format(
                location=self.product_id.property_stock_production.name,
                product=self.product_id.name,)

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
    def check_create_adjustment_accounting_entry(self, amount):
        self.ensure_one()
        # /!\ NOTE: Using accounting approach instead of logistical approach
        aml_obj = self.env['account.move.line']

        location_id = self.product_id.property_stock_production
        account_in_id = location_id.valuation_in_account_id.id
        account_out_id = location_id.valuation_out_account_id.id

        aml_ids = aml_obj.search(
            [('production_id', '=', self.id),
             '|',
             ('account_id', '=', account_in_id),
             ('account_id', '=', account_out_id)])

        amount_consumed = 0.0
        amount_produced = 0.0
        for aml_brw in aml_ids:
            amount_consumed += aml_brw.debit
            amount_produced += aml_brw.credit

        return amount + amount_consumed - amount_produced

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
    def _create_adjustment_account_move_line(
            self, move_id, production_account_id, valuation_account_id, diff):
        """
        Generate the account.move.line values to track the production cost.
        """
        self.ensure_one()
        aml_obj = self.env['account.move.line']

        base_line = dict(
            move_id=move_id.id,
            production_id=self.id,
            name=self.product_id.name + _(' (Valuation Adjustment)'),
            product_id=self.product_id.id,)

        if diff > 0:
            debit_line = dict(
                base_line,
                debit=diff,
                account_id=valuation_account_id,)
            credit_line = dict(
                base_line,
                credit=diff,
                account_id=production_account_id,)
        else:
            debit_line = dict(
                base_line,
                debit=-diff,
                account_id=production_account_id,)
            credit_line = dict(
                base_line,
                credit=-diff,
                account_id=valuation_account_id,)

        aml_obj.create(debit_line)
        aml_obj.create(credit_line)
        return True

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
                production_id=self.id,
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
                    analytic_account_id=wc.costs_cycle_account_id.id,
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
                    analytic_account_id=wc.costs_hour_account_id.id,
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

    @api.multi
    def _create_adjustment_accounting_entries(self, move_id, diff):
        self.ensure_one()
        ctx = dict(self._context)
        template_obj = self.pool.get('product.template')
        production_account_id = self.product_id.property_stock_production.\
            valuation_in_account_id.id
        accounts = template_obj.get_product_accounts(
            self._cr, self._uid, self.product_id.product_tmpl_id.id,
            context=ctx)
        # NOTE: make different between (REAL, AVG) and STD products
        # STD diff shall be booked onto a deviation account
        valuation_account_id = accounts['property_stock_valuation_account_id']

        if self.product_id.cost_method == 'standard':
            company_brw = self.env.user.company_id
            gain_id = \
                company_brw.gain_inventory_deviation_account_id.id
            loss_id = \
                company_brw.loss_inventory_deviation_account_id.id

            if not all([gain_id, loss_id]):
                raise except_orm(
                    _('Error!'),
                    _('Please configure Gain & Loss Inventory Valuation in '
                      'your Company'))

            valuation_account_id = loss_id if diff > 0 else gain_id

        return self._create_adjustment_account_move_line(
            move_id, production_account_id, valuation_account_id, diff)

    # TODO: Should this be moved to a new module?
    @api.multi
    def adjust_quant_cost(self, diff):
        self.ensure_one()
        # NOTE: this apply to AVG, REAL not to STD
        if self.product_id.cost_method == 'standard':
            return True

        all_quants = [quant for raw_mat in self.move_created_ids2
                      for quant in raw_mat.quant_ids]
        qty = sum([quant.qty for quant in all_quants])
        cost = sum([quant2.cost * quant2.qty for quant2 in all_quants])

        for quant in all_quants:
            quant.write({'cost': (cost + diff) / qty})
        return True

    # TODO: Should this be moved to a new module?
    @api.v7
    def costs_generate(self, cr, uid, ids):
        '''
        Method to be used by a Web Service
        It returns id of Journal Entry that was created for Cost Generated
        '''
        ids = isinstance(ids, (int, long)) and ids or ids[0]
        production = self.browse(cr, uid, ids)
        if not production.workcenter_lines:
            self.ws_action_compute_lines(cr, uid, [ids])
        if production.state != 'done':
            return False
        if production.account_move_id:
            return False
        if not production.routing_id:
            if not production.bom_id.routing_id:
                return False
            production.write({'routing_id': production.bom_id.routing_id.id})
        self._costs_generate(cr, uid, production)
        res = production.account_move_id and \
            production.account_move_id.id or False
        return res

    @api.v7
    def _costs_generate(self, cr, uid, production):
        """ Calculates total costs at the end of the production.
        @param production: Id of production order.
        @return: Calculated amount.
        """
        amount = self.check_create_accounting_entry(cr, uid, production.id)

        diff = self.check_create_adjustment_accounting_entry(
            cr, uid, production.id, amount)

        # /!\ NOTE: If product is not real_time Do Not Create Journal Entries
        if production.product_id.valuation == 'real_time' and \
                any([amount, diff]):
            move_id = self._create_account_move(cr, uid, production.id)
            production.write({'account_move_id': move_id.id})

            if amount:
                self._create_accounting_entries(
                    cr, uid, production.id, move_id)
            if diff:
                # NOTE: Subproduct are not taken into accounting in this
                # approach
                # NOTE: make different between (REAL, AVG) and STD products
                # STD diff shall be booked onto a deviation account
                self._create_adjustment_accounting_entries(
                    cr, uid, production.id, move_id, diff)

        if diff:
            # TODO: if product produced is AVG recompute avg value
            # NOTE: Recompute quant cost if not STD
            self.adjust_quant_cost(cr, uid, production.id, diff)

        self.refresh_quant(cr, uid, production, amount, diff)

        return amount

    @api.v7
    def refresh_quant(self, cr, uid, production, amount, diff):
        """
        Method that allow to refresh values for quant & segmentation costs
        """
        return True
