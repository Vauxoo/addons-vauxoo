# -*- coding: utf-8 -*-

from __future__ import division
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning as UserError
import openerp.addons.decimal_precision as dp
from openerp.tools import float_round, float_is_zero


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'
    invoice_ids = fields.One2many(
        'account.invoice',
        'stock_landed_cost_id',
        string='Invoices',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Invoices which contain items to be used as landed costs',
        copy=False,
    )
    move_ids = fields.Many2many(
        'stock.move',
        'stock_landed_move_rel',
        'stock_landed_cost_id',
        'move_id',
        string='Production Moves',
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain=[('production_id', '!=', False), ('state', 'in', ('done',))],
        help='Production Moves to be increased in costs',
        copy=False,
    )

    def lcost_from_inv_line(self, inv_line):
        """Returns a dictionary to create a Landed Cost Line object, based on
        data obtained from the Invoice Line passed as argument"""
        invoice = inv_line.invoice_id
        company_currency = invoice.company_id.currency_id
        currency = invoice.currency_id.with_context(date=invoice.date_invoice)
        price_subtotal = currency.compute(
            inv_line.price_subtotal, company_currency)
        return {
            'name': inv_line.name,
            'account_id': inv_line.account_id and
            inv_line.account_id.id,
            'product_id': inv_line.product_id and
            inv_line.product_id.id,
            'price_unit': price_subtotal,
            'split_method': 'by_quantity',
        }

    @api.onchange('invoice_ids')
    def onchange_invoice_ids(self):
        for lc_brw in self:
            lc_brw.update({'cost_lines': [(6, False, {})]})
            cost_lines = []
            for inv_brw in lc_brw.invoice_ids:
                for ail_brw in inv_brw.invoice_line:
                    if not ail_brw.product_id:
                        continue
                    if not ail_brw.product_id.landed_cost_ok:
                        continue
                    cost_lines.append(
                        (0, False, self.lcost_from_inv_line(ail_brw)))
            if cost_lines:
                lc_brw.update({'cost_lines': cost_lines})

    @api.multi
    def get_costs_from_invoices(self):
        """Update Costs Lines with Invoice Lines in the Invoices related to
        Document
        """
        slcl_obj = self.env['stock.landed.cost.lines']
        for lc_brw in self:
            for cl_brw in lc_brw.cost_lines:
                cl_brw.unlink()
            for inv_brw in lc_brw.invoice_ids:
                company_currency = inv_brw.company_id.currency_id
                diff_currency = inv_brw.currency_id != company_currency
                if diff_currency:
                    currency = inv_brw.currency_id.with_context(
                        date=inv_brw.date_invoice)
                for ail_brw in inv_brw.invoice_line:
                    if not ail_brw.product_id:
                        continue
                    if not ail_brw.product_id.landed_cost_ok:
                        continue
                    if diff_currency:
                        price_subtotal = currency.compute(
                            ail_brw.price_subtotal, company_currency)
                    else:
                        price_subtotal = ail_brw.price_subtotal
                    vals = {
                        'cost_id': lc_brw.id,
                        'name': ail_brw.name,
                        'account_id': ail_brw.account_id and
                        ail_brw.account_id.id,
                        'product_id': ail_brw.product_id and
                        ail_brw.product_id.id,
                        'price_unit': price_subtotal,
                        'split_method': 'by_quantity',
                    }
                    slcl_obj.create(vals)
        return True

    @api.multi
    def get_valuation_lines(self, picking_ids=None):
        """It returns product valuations based on picking's moves
        """
        picking_obj = self.env['stock.picking']
        lines = []
        if not picking_ids and not self.move_ids:
            return lines

        # NOTE: Now it is valid for all costing methods available
        move_ids = [
            move_id
            for picking in picking_obj.browse(picking_ids)
            for move_id in picking.move_lines
            if move_id.product_id.valuation == 'real_time'
        ]

        move_ids += [
            move_id
            for move_id in self.move_ids
            if move_id.product_id.valuation == 'real_time'
        ]

        for move in move_ids:
            total_cost = 0.0

            weight = move.product_id and \
                move.product_id.weight * move.product_qty
            volume = move.product_id and \
                move.product_id.volume * move.product_qty
            for quant in move.quant_ids:
                total_cost += quant.cost * quant.qty
            vals = dict(
                product_id=move.product_id.id,
                move_id=move.id,
                quantity=move.product_uom_qty,
                former_cost=total_cost,
                weight=weight,
                volume=volume)
            lines.append(vals)
        if not lines:
            raise except_orm(
                _('Error!'),
                _('The selected picking does not contain any move that would '
                  'be impacted by landed costs. Landed costs are only possible'
                  ' for products configured in real time valuation. Please '
                  'make sure it is the case, or you selected the correct '
                  'picking.'))
        return lines

    def _create_deviation_account_move_line(
            self, move_id, gain_account_id, loss_account_id,
            valuation_account_id, diff, product_brw):
        """It generates journal items to track landed costs
        """
        ctx = dict(self._context)
        aml_obj = self.pool.get('account.move.line')

        base_line = {
            'move_id': move_id,
            'product_id': product_brw.id,
        }

        name = u'%(name)s: %(memo)s - AVG'

        if diff < 0:
            name = name % dict(
                name=product_brw.name,
                memo=_('Losses on Inventory Deviation'))
            debit_line = dict(
                base_line,
                name=name,
                account_id=loss_account_id,
                debit=-diff,)
            credit_line = dict(
                base_line,
                name=name,
                account_id=valuation_account_id,
                credit=-diff,)
        else:
            name = name % dict(
                name=product_brw.name,
                memo=_('Gains on Inventory Deviation'))
            debit_line = dict(
                base_line,
                name=name,
                account_id=valuation_account_id,
                credit=diff,)
            credit_line = dict(
                base_line,
                name=name,
                account_id=gain_account_id,
                debit=diff,)
        aml_obj.create(
            self._cr, self._uid, debit_line, context=ctx, check=False)
        aml_obj.create(
            self._cr, self._uid, credit_line, context=ctx, check=False)
        return True

    def _get_deviation_accounts(self, product_id, acc_prod):
        """This method takes the variation in value for average and books it as
        Inventory Valuation Deviation
        """
        accounts = acc_prod[product_id]
        valuation_account_id = accounts['property_stock_valuation_account_id']

        company_brw = self.env.user.company_id
        gain_account_id = company_brw.gain_inventory_deviation_account_id.id
        loss_account_id = company_brw.loss_inventory_deviation_account_id.id

        if not gain_account_id or not loss_account_id:
            raise except_orm(
                _('Error!'),
                _('Please configure Gain & Loss Inventory Valuation in your'
                  ' Company'))

        return valuation_account_id, gain_account_id, loss_account_id

    def _create_deviation_accounting_entries(
            self, move_id, product_id, diff, acc_prod=None):
        """This method takes the variation in value for average and books it as
        Inventory Valuation Deviation
        """
        precision_obj = self.pool.get('decimal.precision').precision_get(
            self._cr, self._uid, 'Account')
        if float_is_zero(diff, precision_obj):
            return True
        # TODO: improve code to profit from acc_prod dictionary
        # and reduce overhead with this repetitive query
        valuation_account_id, gain_account_id, loss_account_id = \
            self._get_deviation_accounts(product_id, acc_prod)

        product_brw = self.env['product.product'].browse(product_id)

        return self._create_deviation_account_move_line(
            move_id, gain_account_id, loss_account_id,
            valuation_account_id, diff, product_brw)

    def _create_standard_deviation_entry_lines(
            self, line, move_id, valuation_account_id, gain_account_id,
            loss_account_id):
        """It generates journal items to track landed costs, using arbitrary
        accounts for valuation, gain and loss
        """
        aml_obj = self.env['account.move.line']
        base_line = {
            'name': line.name,
            'move_id': move_id,
            'product_id': line.product_id.id,
            'quantity': line.quantity,
        }
        debit_line = dict(base_line)
        credit_line = dict(base_line)
        diff = line.additional_landed_cost
        if diff > 0:
            debit_line['account_id'] = loss_account_id
            debit_line['debit'] = diff
            credit_line['account_id'] = line.cost_line_id.account_id.id
            credit_line['credit'] = diff
        else:
            # negative cost, reverse the entry
            debit_line['account_id'] = line.cost_line_id.account_id.id
            debit_line['debit'] = -diff
            credit_line['account_id'] = gain_account_id
            credit_line['credit'] = -diff
        aml_obj.create(debit_line, check=False)
        aml_obj.create(credit_line, check=False)
        return True

    @api.multi
    def _create_standard_deviation_entries(self, line, move_id, acc_prod=None):
        """Create standard deviation journal items based on predefined product
        account valuation, gain and loss company's accounts
        """
        if float_is_zero(
                line.additional_landed_cost,
                self.pool.get('decimal.precision').precision_get(
                    self._cr, self._uid, 'Account')):
            return False

        valuation_account_id, gain_account_id, loss_account_id = \
            self._get_deviation_accounts(line.product_id.id, acc_prod)

        return self._create_standard_deviation_entry_lines(
            line, move_id, valuation_account_id, gain_account_id,
            loss_account_id)

    @api.multi
    def _create_cogs_accounting_entries(
            self, product_id, move_id, diff, acc_prod=None):
        """This method takes the amount of cost that needs to be booked as
        inventory value and later takes the amount of COGS that is needed to
        book if any sale was done because of this landing cost been applied
        """
        precision_obj = self.pool.get('decimal.precision').precision_get(
            self._cr, self._uid, 'Account')
        if float_is_zero(diff, precision_obj):
            return True
        product_brw = self.env['product.product'].browse(product_id)
        accounts = acc_prod[product_id]
        debit_account_id = accounts['property_stock_valuation_account_id']
        # NOTE: BEWARE of accounts when account_anglo_saxon applies
        # TODO: Do we have to set another account for cogs_account_id?
        cogs_account_id = \
            product_brw.property_account_expense and \
            product_brw.property_account_expense.id or \
            product_brw.categ_id.property_account_expense_categ and \
            product_brw.categ_id.property_account_expense_categ.id

        if not cogs_account_id:
            raise except_orm(
                _('Error!'),
                _('Please configure Stock Expense Account for product: %s.') %
                (product_brw.name))

        return self._create_cogs_account_move_line(
            product_brw, move_id, debit_account_id, cogs_account_id, diff)

    @api.multi
    def _create_cogs_account_move_line(
            self, product_brw, move_id, debit_account_id, cogs_account_id,
            diff):
        """Create journal items for COGS for those products sold
        before landed costs were applied
        """

        ctx = dict(self._context)
        aml_obj = self.pool.get('account.move.line')
        base_line = {
            'move_id': move_id,
            'product_id': product_brw.id,
        }
        # Create COGS account move lines for products that were sold prior to
        # applying landing costs
        # NOTE: knowing how many products that were affected, COGS was to
        # change, by this landed cost is not really necessary

        name = u'%(name)s: COGS - %(memo)s'
        if diff > 0:
            name = name % dict(name=product_brw.name, memo='[+]')
            debit_line = dict(
                base_line,
                name=name,
                account_id=cogs_account_id,
                debit=diff,)
            credit_line = dict(
                base_line,
                name=name,
                account_id=debit_account_id,
                credit=diff,)
        else:
            # /!\ NOTE: be careful when making reversions on landed costs or
            # negative landed costs
            name = name % dict(name=product_brw.name, memo='[-]')
            debit_line = dict(
                base_line,
                name=name,
                account_id=debit_account_id,
                debit=-diff,)
            credit_line = dict(
                base_line,
                name=name,
                account_id=cogs_account_id,
                credit=-diff,)

        aml_obj.create(
            self._cr, self._uid, debit_line, context=ctx, check=False)
        aml_obj.create(
            self._cr, self._uid, credit_line, context=ctx, check=False)
        return True

    def compute_average_cost(self, dct=None):
        """This method updates standard_price field in products with costing
        method equal to average
        """
        dct = dict(dct or {})
        if not dct:
            return True
        scp_obj = self.env['stock.card.product']
        for product_id, field2write in dct.items():
            scp_obj.write_standard_price(product_id, field2write)
        return True

    @api.v8
    def _check_button_validate(self):
        if self.state != 'draft':
            raise UserError(
                _('Only draft landed costs can be validated'))
        if not self.valuation_adjustment_lines or \
                not self._check_sum(self):
            raise UserError(
                _('You cannot validate a landed cost which has no valid '
                    'valuation adjustments lines. Did you click on '
                    'Compute?'))
        return True

    @api.multi
    # @do_profile(follow=[])
    def button_validate(self):
        self.ensure_one()
        quant_obj = self.env['stock.quant']
        template_obj = self.pool.get('product.template')
        scp_obj = self.env['stock.card.product']
        get_average = scp_obj.get_average
        stock_card_move_get = scp_obj._stock_card_move_get
        ctx = dict(self._context)

        for cost in self:
            cost._check_button_validate()

            move_id = self._model._create_account_move(
                self._cr, self._uid, cost, context=ctx)
            prod_dict = {}
            init_avg = {}
            first_lines = {}
            first_card = {}
            prod_qty = {}
            acc_prod = {}
            quant_dict = {}
            # TODO: To be replaced by a new API filtered feature
            val_gen = (ln for ln in cost.valuation_adjustment_lines
                       if ln.move_id and
                       ln.move_id.location_id.usage != 'internal')
            for line in val_gen:

                product_id = line.product_id

                if product_id.id not in acc_prod:
                    acc_prod[product_id.id] = \
                        template_obj.get_product_accounts(
                        self._cr, self._uid, product_id.product_tmpl_id.id,
                        context=ctx)

                if product_id.cost_method == 'standard':
                    self._create_standard_deviation_entries(
                        line, move_id, acc_prod)
                    continue

                if product_id.cost_method == 'average' and \
                        product_id.id not in prod_dict:
                    first_card = stock_card_move_get(product_id.id)
                    prod_dict[product_id.id] = True
                    first_lines[product_id.id] = first_card['res']
                    init_avg[product_id.id] = product_id.standard_price
                    prod_qty[product_id.id] = first_card['product_qty']

                per_unit = line.final_cost / line.quantity
                diff = per_unit - line.former_cost_per_unit
                quants = [quant for quant in line.move_id.quant_ids]
                for quant in quants:
                    if quant.id not in quant_dict:
                        quant_dict[quant.id] = quant.cost + diff
                    else:
                        quant_dict[quant.id] += diff

                # TODO: To be replaced by a new API filtered feature
                qty_out = sum(
                    [quant.qty
                     for quant in line.move_id.quant_ids
                     if quant.location_id.usage != 'internal' and
                     product_id.cost_method == 'real'])

                # /!\ NOTE: Inventory valuation
                # qty_out will be zero with product_id.cost_method == 'average'
                self._create_landed_accounting_entries(
                    line, move_id, qty_out, acc_prod)

            for key, value in quant_dict.items():
                quant_obj.sudo().browse(key).write(
                    {'cost': value})

            # /!\ NOTE: COGS computation
            # NOTE: After adding value to product with landing cost products
            # with costing method `average` need to be check in order to
            # find out the change in COGS in case of sales were performed prior
            # to landing costs
            for prod_id in prod_dict:
                last_card = stock_card_move_get(prod_id)
                prod_dict[prod_id] = get_average(last_card)
                fst_avg = lst_avg = diff = 0.0
                ini_avg = init_avg[prod_id]
                for first, last in zip(first_lines[prod_id], last_card['res']):
                    fst_avg = first['average']
                    lst_avg = last['average']
                    if first['qty'] >= 0:
                        # /!\ TODO: This is not true for devolutions
                        continue

                    # NOTE: Rounding problems could arise here, this needs to
                    # be checked
                    diff += (lst_avg - fst_avg) * abs(first['qty'])
                self._create_cogs_accounting_entries(
                    prod_id, move_id, diff, acc_prod)

                # TODO: Compute deviation
                # /!\ NOTE:
                # - ini_avg: is the average initially written in product
                # - fst_avg: is the average initially computed with stock card
                # - lst_avg: is the average lately computed with stock card
                diff = (fst_avg - ini_avg) * prod_qty[prod_id]
                if lst_avg != ini_avg:
                    # /!\ NOTE:
                    # if lst_avg == ini_avg:
                    #     the difference fst_avg - ini_avg has already been
                    #     written with increased inventory
                    self._create_deviation_accounting_entries(
                        move_id, prod_id, diff, acc_prod)

            # TODO: Write latest value for average
            cost.compute_average_cost(prod_dict)

            cost.write(
                {'state': 'done', 'account_move_id': move_id})

            # Post the account move if the journal's auto post true
            move_obj = self.env['account.move'].browse(move_id)
            if move_obj.journal_id.entry_posted:
                move_obj.post()
                move_obj.validate()

        return True

    @api.v7
    def compute_landed_cost(self, cr, uid, ids, context=None):
        """It compute valuation lines for landed costs based on
        splitting method used
        """
        line_obj = self.pool.get('stock.valuation.adjustment.lines')
        unlink_ids = line_obj.search(
            cr, uid, [('cost_id', 'in', ids)], context=context)
        line_obj.unlink(cr, uid, unlink_ids, context=context)
        digits = dp.get_precision('Product Price')(cr)
        towrite_dict = {}
        for cost in self.browse(cr, uid, ids, context=None):
            if not cost.picking_ids and not cost.move_ids:
                continue
            picking_ids = [p.id for p in cost.picking_ids]
            total_qty = 0.0
            total_cost = 0.0
            total_weight = 0.0
            total_volume = 0.0
            total_line = 0.0
            vals = self.get_valuation_lines(
                cr, uid, [cost.id], picking_ids, context=context)
            for v in vals:
                for line in cost.cost_lines:
                    v.update({'cost_id': cost.id, 'cost_line_id': line.id})
                    line_obj.create(cr, uid, v, context=context)
                total_qty += v.get('quantity', 0.0)
                total_cost += v.get('former_cost', 0.0)
                total_weight += v.get('weight', 0.0)
                total_volume += v.get('volume', 0.0)
                total_line += 1

            for line in cost.cost_lines:
                value_split = 0.0
                for valuation in cost.valuation_adjustment_lines:
                    value = 0.0
                    if valuation.cost_line_id and \
                            valuation.cost_line_id.id == line.id:
                        if line.split_method == 'by_quantity' and total_qty:
                            per_unit = (line.price_unit / total_qty)
                            value = valuation.quantity * per_unit
                        elif line.split_method == 'by_weight' and total_weight:
                            per_unit = (line.price_unit / total_weight)
                            value = valuation.weight * per_unit
                        elif line.split_method == 'by_volume' and total_volume:
                            per_unit = (line.price_unit / total_volume)
                            value = valuation.volume * per_unit
                        elif line.split_method == 'equal':
                            value = (line.price_unit / total_line)
                        elif line.split_method == 'by_current_cost_price' and \
                                total_cost:
                            per_unit = (line.price_unit / total_cost)
                            value = valuation.former_cost * per_unit
                        else:
                            value = (line.price_unit / total_line)

                        if digits:
                            value = float_round(
                                value, precision_digits=digits[1],
                                rounding_method='UP')
                            fnc = min if line.price_unit > 0 else max
                            value = fnc(value, line.price_unit - value_split)
                            value_split += value

                        if valuation.id not in towrite_dict:
                            towrite_dict[valuation.id] = value
                        else:
                            towrite_dict[valuation.id] += value
        if towrite_dict:
            for key, value in towrite_dict.items():
                line_obj.write(
                    cr, uid, key, {'additional_landed_cost': value},
                    context=context)
        return True

    @api.v8
    def compute_landed_cost(self):  # pylint: disable=E0102
        return self._model.compute_landed_cost(self._cr, self._uid, self.ids)

    def _create_landed_account_move_line(
            self, line, move_id, credit_account_id, debit_account_id, qty_out,
            already_out_account_id):
        """Generate the account.move.line values to track the landed cost.
        Afterwards, for the goods that are already out of stock, we should
        create the out moves
        """
        ctx = dict(self._context)
        cr, uid = self._cr, self._uid
        aml_obj = self.pool.get('account.move.line')
        base_line = {
            'name': line.name,
            'move_id': move_id,
            'product_id': line.product_id.id,
            'quantity': line.quantity,
        }
        debit_line = dict(base_line, account_id=debit_account_id)
        credit_line = dict(base_line, account_id=credit_account_id)
        diff = line.additional_landed_cost
        if diff > 0:
            debit_line['debit'] = diff
            credit_line['credit'] = diff
        elif diff < 0:
            # negative cost, reverse the entry
            debit_line['credit'] = -diff
            credit_line['debit'] = -diff
        if diff != 0:
            aml_obj.create(cr, uid, debit_line, context=ctx, check=False)
            aml_obj.create(cr, uid, credit_line, context=ctx, check=False)

        # Create account move lines for quants already out of stock
        if qty_out > 0:
            debit_line = dict(
                debit_line,
                name=(line.name + ": " + str(qty_out) + _(' already out')),
                quantity=qty_out,
                account_id=already_out_account_id)
            credit_line = dict(
                credit_line,
                name=(line.name + ": " + str(qty_out) + _(' already out')),
                quantity=qty_out,
                account_id=debit_account_id)
            diff = diff * qty_out / line.quantity
            if diff > 0:
                debit_line['debit'] = diff
                credit_line['credit'] = diff
            elif diff < 0:
                # negative cost, reverse the entry
                debit_line['credit'] = -diff
                credit_line['debit'] = -diff
            if diff != 0:
                aml_obj.create(
                    cr, uid, debit_line, context=ctx, check=False)
                aml_obj.create(
                    cr, uid, credit_line, context=ctx, check=False)
        return True

    def _create_landed_accounting_entries(
            self, line, move_id, qty_out, acc_prod=None):
        cost_product = line.cost_line_id and line.cost_line_id.product_id
        if not cost_product:
            return False

        accounts = acc_prod[line.product_id.id]

        debit_account_id = accounts['property_stock_valuation_account_id']
        already_out_account_id = accounts['stock_account_output']

        # /!\ NOTE: This can be optimized by providing the accounts in a dict
        credit_account_id = line.cost_line_id.account_id.id or \
            cost_product.property_account_expense.id or \
            cost_product.categ_id.property_account_expense_categ.id

        if not credit_account_id:
            raise except_orm(
                _('Error!'),
                _('Please configure Stock Expense Account for product: %s.') %
                (cost_product.name))

        return self._create_landed_account_move_line(
            line, move_id, credit_account_id, debit_account_id, qty_out,
            already_out_account_id)
