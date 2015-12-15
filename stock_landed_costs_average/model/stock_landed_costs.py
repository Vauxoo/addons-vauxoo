# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp import osv
from openerp.exceptions import except_orm, Warning as UserError
import openerp.addons.decimal_precision as dp
from openerp.tools import float_round


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

    @api.multi
    def get_costs_from_invoices(self):
        '''
        Update Costs Lines with Invoice Lines in the Invoices related to
        Document
        '''
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
        picking_obj = self.env['stock.picking']
        lines = []
        if not picking_ids and not self.move_ids:
            return lines

        move_ids = [
            move_id
            for picking in picking_obj.browse(picking_ids)
            for move_id in picking.move_lines
            if move_id.product_id.valuation == 'real_time' and
            move_id.product_id.cost_method in ('average', 'real')
            ]

        move_ids += [
            move_id
            for move_id in self.move_ids
            if move_id.product_id.valuation == 'real_time' and
            move_id.product_id.cost_method in ('average', 'real')
            ]

        for move in move_ids:
            total_cost = 0.0
            total_qty = move.product_qty
            weight = move.product_id and \
                move.product_id.weight * move.product_qty
            volume = move.product_id and \
                move.product_id.volume * move.product_qty
            for quant in move.quant_ids:
                total_cost += quant.cost
            vals = dict(
                product_id=move.product_id.id,
                move_id=move.id,
                quantity=move.product_uom_qty,
                former_cost=total_cost * total_qty,
                weight=weight,
                volume=volume)
            lines.append(vals)
        if not lines:
            raise except_orm(
                _('Error!'),
                _('The selected picking does not contain any move that would '
                  'be impacted by landed costs. Landed costs are only possible'
                  ' for products configured in real time valuation with real'
                  ' price or average costing method. Please make sure it is '
                  'the case, or you selected the correct picking'))
        return lines

    def _create_deviation_account_move_line(
            self, move_id, gain_account_id, loss_account_id,
            valuation_account_id, diff, product_brw):
        # TODO: Change DocString
        """
        Generate the account.move.line values to track the landed cost.
        Afterwards, for the goods that are already out of stock, we should
        create the out moves
        """
        ctx = dict(self._context)
        aml_obj = self.pool.get('account.move.line')

        base_line = {
            'move_id': move_id,
            'product_id': product_brw.id,
        }

        if diff > 0:
            name = product_brw.name + ": " + _('Gains on Inventory Deviation')
            debit_line = dict(
                base_line,
                name=name,
                account_id=valuation_account_id,
                debit=diff,)
            credit_line = dict(
                base_line,
                name=name,
                account_id=gain_account_id,
                credit=diff,)
        else:
            name = product_brw.name + ": " + _('Losses on Inventory Deviation')
            debit_line = dict(
                base_line,
                name=name,
                account_id=loss_account_id,
                credit=-diff,)
            credit_line = dict(
                base_line,
                name=name,
                account_id=valuation_account_id,
                debit=-diff,)
            # negative cost, reverse the entry
        aml_obj.create(self._cr, self._uid, debit_line, context=ctx)
        aml_obj.create(self._cr, self._uid, credit_line, context=ctx)
        return True

    def _create_deviation_accounting_entries(
            self, move_id, product_id, old_avg, new_avg, qty):
        '''
        This method takes the variation in value for average and books it as
        Inventory Valuation Deviation
        '''
        product_obj = self.env['product.product']
        template_obj = self.pool.get('product.template')
        if not abs(old_avg - new_avg) or not qty:
            return False
        ctx = dict(self._context)
        product_brw = product_obj.browse(product_id)
        accounts = template_obj.get_product_accounts(
            self._cr, self._uid, product_brw.product_tmpl_id.id, context=ctx)
        valuation_account_id = accounts['property_stock_valuation_account_id']

        # TODO: Accounts for gains & losses because of change in inventory
        # valuation show be set in company
        gain_account_id = accounts['stock_account_output']
        loss_account_id = accounts['stock_account_input']

        if not gain_account_id or not loss_account_id:
            raise osv.except_osv(
                _('Error!'),
                _('Please configure Gain & Loss Inventory Valuation in your'
                  ' Company'))

        amount = (old_avg - new_avg) * qty

        return self._create_deviation_account_move_line(
            move_id, gain_account_id, loss_account_id,
            valuation_account_id, amount, product_brw)

    @api.multi
    def _create_cogs_accounting_entries(self, line, move_id, old_avg, new_avg):
        '''
        This method takes the amount of cost that needs to be booked as
        inventory value and later takes the amount of COGS that is needed to
        book if any sale was done because of this landing cost been applied
        '''
        product_obj = self.pool.get('product.template')
        cost_product = line.cost_line_id and line.cost_line_id.product_id
        if not cost_product:
            return False
        ctx = dict(self._context)
        accounts = product_obj.get_product_accounts(
            self._cr, self._uid, line.product_id.product_tmpl_id.id,
            context=ctx)
        debit_account_id = accounts['property_stock_valuation_account_id']
        # NOTE: BEWARE of accounts when account_anglo_saxon applies
        # TODO: Do we have to set another account for cogs_account_id?
        cogs_account_id = accounts['stock_account_output']
        credit_account_id = line.cost_line_id.account_id.id or \
            cost_product.property_account_expense.id or \
            cost_product.categ_id.property_account_expense_categ.id

        if not credit_account_id:
            raise osv.except_osv(
                _('Error!'),
                _('Please configure Stock Expense Account for product: %s.') %
                (cost_product.name))

        return self._create_cogs_account_move_line(
            line, move_id, credit_account_id, debit_account_id,
            cogs_account_id, old_avg, new_avg)

    @api.multi
    def _create_cogs_account_move_line(
            self, line, move_id, credit_account_id, debit_account_id,
            cogs_account_id, old_avg, new_avg):
        # TODO: Change DocString
        """
        Generate the account.move.line values to track the landed cost.
        Afterwards, for the goods that are already out of stock, we should
        create the out moves
        """

        ctx = dict(self._context)
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
        else:
            # negative cost, reverse the entry
            debit_line['credit'] = -diff
            credit_line['debit'] = -diff
        aml_obj.create(self._cr, self._uid, debit_line, context=ctx)
        aml_obj.create(self._cr, self._uid, credit_line, context=ctx)

        # Create COGS account move lines for products that were sold prior to
        # applying landing costs
        # TODO: Rounding problems could arise here, this needs to be checked
        diff = new_avg - old_avg
        if not abs(diff):
            return True

        # NOTE: knowing how many products that were affected, COGS was to
        # change, by this landed cost is not really necessary
        debit_line = dict(
            debit_line,
            name=(line.name + ": " + _(' COGS')),
            account_id=cogs_account_id)
        credit_line = dict(
            credit_line,
            name=(line.name + ": " + _(' [COGS] already out')),
            account_id=debit_account_id)
        if diff > 0:
            debit_line['debit'] = diff
            credit_line['credit'] = diff
        else:
            # negative cost, reverse the entry
            debit_line['credit'] = -diff
            credit_line['debit'] = -diff
        aml_obj.create(self._cr, self._uid, debit_line, context=ctx)
        aml_obj.create(self._cr, self._uid, credit_line, context=ctx)
        return True

    def compute_average_cost(self, move_id, dct=None):
        '''
        This method updates standard_price field in products with costing
        method equal to average
        '''
        dct = dict(dct or {})
        if not dct:
            return True

        product_obj = self.env['product.product']
        get_qty = self.env['stock.card.product'].get_qty

        for product_id, avg in dct.iteritems():
            # Write the standard price, as SUDO because a warehouse
            # manager may not have the right to write on products
            product_brw = product_obj.sudo().browse(product_id)

            # NOTE: if there is a variation among avg and standard_price set on
            # product new Journal Entry Lines shall be created
            qty = get_qty(product_id)
            self._create_deviation_accounting_entries(
                move_id, product_id,
                product_brw.standard_price, avg, qty)

            product_obj.sudo().browse(product_id).write(
                {'standard_price': avg})
        return True

    @api.multi
    def button_validate(self):
        self.ensure_one()
        quant_obj = self.env['stock.quant']
        get_average = self.env['stock.card.product'].get_average
        ctx = dict(self._context)

        for cost in self:
            if cost.state != 'draft':
                raise UserError(
                    _('Only draft landed costs can be validated'))
            if not cost.valuation_adjustment_lines or \
                    not self._check_sum(cost):
                raise UserError(
                    _('You cannot validate a landed cost which has no valid '
                      'valuation adjustments lines. Did you click on '
                      'Compute?'))

            move_id = self._model._create_account_move(
                self._cr, self._uid, cost, context=ctx)
            quant_dict = {}
            prod_dict = {}
            for line in cost.valuation_adjustment_lines:
                if not line.move_id:
                    continue
                product_id = line.product_id
                if product_id.cost_method == 'average':
                    if product_id.id not in prod_dict:
                        prod_dict[product_id.id] = get_average(product_id.id)

                per_unit = line.final_cost / line.quantity
                diff = per_unit - line.former_cost_per_unit
                quants = [quant for quant in line.move_id.quant_ids]
                for quant in quants:
                    if quant.id not in quant_dict:
                        quant_dict[quant.id] = quant.cost + diff
                    else:
                        quant_dict[quant.id] += diff
                for key, value in quant_dict.items():
                    quant_obj.browse(key).write(
                        {'cost': value})

                qty_out = 0
                for quant in line.move_id.quant_ids:
                    if quant.location_id.usage != 'internal':
                        qty_out += quant.qty

                if product_id.cost_method == 'average':
                    # NOTE: After adding value to product in its quants average
                    # needs to be recomputed in order to find out the change in
                    # COGS in case of sales were performed prior to landing
                    # costs
                    new_avg = get_average(product_id.id)
                    self._create_cogs_accounting_entries(
                        line, move_id, prod_dict[product_id.id], new_avg)

                if product_id.cost_method != 'real':
                    continue

                self._create_accounting_entries(line, move_id, qty_out)

            cost.compute_average_cost(move_id, prod_dict)

            cost.write(
                {'state': 'done', 'account_move_id': move_id})
        return True

    @api.v7
    def compute_landed_cost(self, cr, uid, ids, context=None):
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
                            value = min(value, line.price_unit - value_split)
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
