# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from pprint import pprint
from openerp.exceptions import except_orm, Warning


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
        if not picking_ids:
            return lines

        for picking in picking_obj.browse(picking_ids):
            for move in picking.move_lines:
                if move.product_id.valuation != 'real_time' or \
                        move.product_id.cost_method != 'average':
                    continue
                total_cost = 0.0
                total_qty = move.product_qty
                weight = move.product_id and \
                    move.product_id.weight * move.product_qty
                volume = move.product_id and \
                    move.product_id.volume * move.product_qty
                for quant in move.quant_ids:
                    total_cost += quant.cost
                vals = dict(product_id=move.product_id.id,
                            move_id=move.id,
                            quantity=move.product_uom_qty,
                            former_cost=total_cost * total_qty,
                            weight=weight,
                            volume=volume)
                lines.append(vals)
        try:
            lines += super(
                StockLandedCost, self).get_valuation_lines(
                    picking_ids=picking_ids)
        except Exception as e:
            pprint(e)
        if not lines:
            raise except_orm(
                _('Error!'),
                _('The selected picking does not contain any move that would '
                  'be impacted by landed costs. Landed costs are only possible'
                  ' for products configured in real time valuation with real'
                  ' price or average costing method. Please make sure it is '
                  'the case, or you selected the correct picking'))
        return lines

    @api.v7
    def _create_account_move_line(
            self, cr, uid, line, move_id, credit_account_id, debit_account_id,
            qty_out, already_out_account_id, context=None):
        # TODO: Change DocString
        """
        Generate the account.move.line values to track the landed cost.
        Afterwards, for the goods that are already out of stock, we should
        create the out moves
        """
        if line.product_id.cost_method != 'average':
            return super(StockLandedCost, self)._create_account_move_line(
                cr, uid, line, move_id, credit_account_id, debit_account_id,
                qty_out, already_out_account_id, context=context)

        # TODO: Create a new function for this option
        domain = [('date', '<=', line.move_id.date)]
        domain += [('product_id', '=', line.product_id.id)]
        field_names = ['product_id', 'quantity']
        sh_obj = self.pool.get('stock.history')
        Q = sh_obj.read_group(cr, uid, domain, field_names, ['product_id'])
        Q = sum(elem['quantity'] for elem in Q)
        # END TODO: Create a new function for this option

        if Q <= 0:
            # If quantity available a that moment is less or equal than zero
            # return True doing nothing
            return True

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
        if (1 - qty_out / Q):
            if diff > 0:
                debit_line['debit'] = diff * (1 - qty_out / Q)
                credit_line['credit'] = diff * (1 - qty_out / Q)
            else:
                # negative cost, reverse the entry
                # TODO: Have to look for an approach when reversing landed cost
                # with average cost_method
                debit_line['credit'] = -diff
                credit_line['debit'] = -diff
            aml_obj.create(cr, uid, debit_line, context=context)
            aml_obj.create(cr, uid, credit_line, context=context)

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
            diff = diff * (qty_out / Q)
            if diff > 0:
                debit_line['debit'] = diff
                credit_line['credit'] = diff
            else:
                # negative cost, reverse the entry
                # TODO: Have to look for an approach when reversing landed cost
                # with average cost_method
                debit_line['credit'] = -diff
                credit_line['debit'] = -diff
            aml_obj.create(cr, uid, debit_line, context=context)
            aml_obj.create(cr, uid, credit_line, context=context)
        return True













    @api.multi
    def compute_average_cost_used_quants(self, move_id, dct):
        '''
        This method updates standard_price field in products with costing
        method equal to average
        '''
        self.ensure_one()
        product_obj = self.env['product.product']
        sm_obj = self.env['stock.move']
        sval_obj = self.env['stock.valuation.adjustment.lines']

        for prod_id, sm_ids in dct.iteritems():
            sm_ids = list(sm_ids)

            sval_ids = []
            for sm_id in sm_obj._search(
                    [('id', 'in', sm_ids)], order='date asc'):

                args = [('cost_id', '=', self.id), ('move_id', '=', sm_id)]
                sval_ids += sval_obj._search(args)

            for sval_id in sval_ids:
                sval_brw = sval_obj.browse(sval_id)
                qty_out = 0
                # TODO: memoize()
                for quant in sval_brw.move_id.quant_ids:
                    if quant.location_id.usage != 'internal':
                        qty_out += quant.qty
                self._create_accounting_entries(sval_brw, move_id, qty_out)


        return True

    @api.multi
    def compute_average_cost(self, move_id, dct):
        '''
        This method updates standard_price field in products with costing
        method equal to average
        '''
        self.ensure_one()
        product_obj = self.env['product.product']

        for cost in self:
            prod_qty_dict = {}
            prod_val_dict = {}
            prod_adj_dict = {}
            for line in cost.valuation_adjustment_lines:
                if not line.move_id:
                    continue

                if line.product_id.cost_method != 'average':
                    continue

                if dct.get(line.product_id.id):
                    # TODO: A new way of computing Average has to be developed
                    # when products have gone prior to allocate landed costs.
                    # This way of computing it does not work
                    continue

                qty_out = 0
                for quant in line.move_id.quant_ids:
                    if quant.location_id.usage != 'internal':
                        qty_out += quant.qty
                self._create_accounting_entries(line, move_id, qty_out)

                # Current quantity of products available
                if not prod_qty_dict.get(line.product_id.id):
                    prod_qty_dict[line.product_id.id] = \
                        line.product_id.product_tmpl_id.qty_available

                # Current valuation of products available
                if not prod_val_dict.get(line.product_id.id):
                    prod_val_dict[line.product_id.id] = \
                        line.product_id.standard_price * \
                        line.product_id.product_tmpl_id.qty_available

                # Current Landed Value for product
                if not prod_adj_dict.get(line.product_id.id):
                    prod_adj_dict[line.product_id.id] = \
                        line.additional_landed_cost
                else:
                    prod_adj_dict[line.product_id.id] += \
                        line.additional_landed_cost

            for k in prod_qty_dict.keys():
                if prod_qty_dict[k] < 0:
                    prod = product_obj.browse(k)
                    raise UserError(
                        _('Product %s has negative quantities' % prod.name))
                if prod_qty_dict[k] == 0.0:
                    continue
                new_std_price = ((prod_val_dict[k] + prod_adj_dict[k]) /
                                 prod_qty_dict[k])
                # Write the standard price, as SUDO because a warehouse
                # manager may not have the right to write on products
                product_obj.sudo().browse(k).write(
                    {'standard_price': new_std_price})
        return True

    @api.multi
    def button_validate(self):
        self.ensure_one()
        quant_obj = self.env['stock.quant']
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

            # TODO: 01 put this piece of code in a new method
            move_id = self._model._create_account_move(
                self._cr, self._uid, cost, context=ctx)
            quant_dict = {}
            prod_dict = {}
            for line in cost.valuation_adjustment_lines:
                if not line.move_id:
                    continue
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

                # TODO: 03
                # THIS CAN BE CALL WHEN COMPUTING AVERAGE WHERE IT IS ACTUALLY
                # USEFUL
                if line.product_id.cost_method != 'real':
                    if line.product_id.id not in prod_dict:
                        prod_dict[line.product_id.id] = set([line.move_id.id])
                    else:
                        prod_dict[line.product_id.id].add(line.move_id.id)
                    continue
                # END OF TODO 03

                self._create_accounting_entries(line, move_id, qty_out)
            # END OF TODO 01

            # TODO: 02 Method to compute standard_price for average cost_method
            cost.compute_average_cost(move_id, prod_dict)
            cost.compute_average_cost_used_quants(move_id, prod_dict)
            # END OF TODO 02

            cost.write(
                {'state': 'done', 'account_move_id': move_id})
        return True
