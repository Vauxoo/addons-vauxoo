from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning as UserError


class MrpProduction(models.Model):

    """Production Orders / Manufacturing Orders
    """
    _inherit = 'mrp.production'
    _description = 'Manufacturing Order'
    account_move_id = fields.Many2one(
        'account.move',
        string='Cost Journal Entry',
        readonly=True,
        copy=False,
    )

    def update_production_journal_items(self):
        mrp_ids = self.search([('state', '=', 'progress')])
        for mrp_brw in mrp_ids:
            aml_ids = []
            for raw_brw in mrp_brw.move_lines2:
                aml_ids += [aml.id for aml in raw_brw.aml_all_ids]
            for fg_brw in mrp_brw.move_created_ids2:
                aml_ids += [aml.id for aml in fg_brw.aml_all_ids]
            if aml_ids:
                self._cr.execute(
                    ''' UPDATE account_move_line
                        SET production_id = %s
                        WHERE id IN %s;''',
                    (mrp_brw.id, tuple(aml_ids)))
        return True

    @api.multi
    def test_accounting_setting(self):
        self.ensure_one()
        msg = ''
        if not self.routing_id:
            msg_journal = _(
                'Please set a Journal in Product Category: {cat} to book '
                'Production Cost Journal Entries\n')
            if not self.product_id.categ_id.property_stock_journal:
                msg += msg_journal.format(cat=self.product_id.categ_id.name)
            if msg:
                raise UserError(msg)
            return True

        company_brw = self.env.user.company_id
        require_workcenter_analytic = company_brw.require_workcenter_analytic

        msg_hour = _('Add Hour Analytical Account on Worcenter: {wc}\n')
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

        for workorder in self.workorder_ids:
            wc = workorder.workcenter_id
            hour_cost = workorder.duration / 60.0 * wc.costs_hour

            if not require_workcenter_analytic:
                continue

            if hour_cost and not wc.costs_hour_account_id:
                msg += msg_hour.format(wc=wc.name)

        if msg:
            raise UserError(msg)

        return True

    @api.multi
    def button_mark_done(self):
        self.ensure_one()
        self.test_accounting_setting()
        return super(MrpProduction, self).button_mark_done()

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
    def _create_account_move(self):
        self.ensure_one()
        am_obj = self.env['account.move']
        date = fields.Date.context_today(self)
        journal_id = self.routing_id and self.routing_id.journal_id or \
            self.product_id.categ_id.property_stock_journal
        vals = {
            'journal_id': journal_id.id,
            'date': date,
            'ref': self.name,
            'company_id': self.company_id.id,
        }
        return am_obj.create(vals)

    @api.multi
    def _create_adjustment_account_move_line(
            self, move_id, production_account_id, valuation_account_id, diff):
        """Generate the account.move.line values to track the production cost.
        """
        self.ensure_one()

        base_line = dict(
            move_id=move_id.id,
            production_id=self.id,
            name=self.product_id.name + _(' (Valuation Adjustment)'),
            product_id=self.product_id.id,)

        debit_line = dict(
            base_line,
            debit=abs(diff),
            account_id=(
                valuation_account_id if diff > 0 else production_account_id))
        credit_line = dict(
            base_line,
            credit=abs(diff),
            account_id=(
                production_account_id if diff > 0 else valuation_account_id))
        move_id.write({
            'line_ids': [
                (0, 0, debit_line),
                (0, 0, credit_line),
            ]
        })
        return True

    @api.multi
    def _create_account_move_line(self, move_id, production_account_id):
        """Generate the account.move.line values to track the production cost.
        """
        self.ensure_one()

        for workorder in self.workorder_ids:
            wc = workorder.workcenter_id
            hours = workorder.duration / 60.0
            hour_cost = hours * wc.costs_hour

            if not hour_cost:
                continue

            base_line = dict(
                move_id=move_id.id,
                production_id=self.id,
                product_id=self.product_id.id,
                product_uom_id=self.product_id and self.product_id.uom_id.id,)

            if hour_cost:
                base_hour = dict(
                    base_line,
                    name=workorder.name + ' (H)',
                    quantity=hours,)
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
                move_id.write({
                    'line_ids': [
                        (0, 0, debit_hour),
                        (0, 0, credit_hour),
                    ]
                })
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
        production_account_id = self.product_id.property_stock_production.\
            valuation_in_account_id.id
        accounts = self.product_id.product_tmpl_id.get_product_accounts()
        # NOTE: make different between (REAL, AVG) and STD products
        # STD diff shall be booked onto a deviation account
        valuation_account_id = accounts['stock_valuation'].id

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

    def _costs_generate(self):
        """ Calculates total costs at the end of the production.
        @return: Calculated amount.
        """
        amount = abs(super(MrpProduction, self)._costs_generate())
        diff = self.check_create_adjustment_accounting_entry(amount)

        # /!\ NOTE: If product is not real_time Do Not Create Journal Entries
        if self.product_id.valuation == 'real_time' and \
                any([amount, diff]):
            move_id = self._create_account_move()
            self.write({'account_move_id': move_id.id})

            if amount:
                self._create_accounting_entries(move_id)
            if diff:
                # NOTE: Subproduct are not taken into accounting in this
                # approach
                # NOTE: make different between (REAL, AVG) and STD products
                # STD diff shall be booked onto a deviation account
                self._create_adjustment_accounting_entries(move_id, diff)
            move_id.post()
        return amount
