# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning as UserError

SEGMENTATION_COST = [
    ('landed_cost', 'Landed Cost'),
    ('subcontracting_cost', 'Subcontracting Cost'),
    ('material_cost', 'Material Cost'),
    ('production_cost', 'Production Cost'),
]


class StockLandedCostLines(models.Model):
    _inherit = 'stock.landed.cost.lines'

    segmentation_cost = fields.Selection(
        SEGMENTATION_COST,
        string='Segmentation',
    )


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
    def button_validate(self):
        self.ensure_one()
        for cost in self:
            if cost.state != 'draft':
                raise UserError(
                    _('Only draft landed costs can be validated'))
            if not cost.valuation_adjustment_lines or \
                    not cost._check_sum():
                raise UserError(
                    _('You cannot validate a landed cost which has no valid '
                      'valuation adjustments lines. Did you click on '
                      'Compute?'))

            if not all([cl.segmentation_cost for cl in cost.cost_lines]):
                raise UserError(
                    _('Please fill the segmentation field in Cost Lines'))

            move_dict = {}
            for line in cost.valuation_adjustment_lines:
                if not line.move_id:
                    continue

                segment = line.cost_line_id.segmentation_cost
                per_unit = line.final_cost / line.quantity
                diff = per_unit - line.former_cost_per_unit

                for move in line.move_id:
                    move_dict[segment] = move[segment] + diff
                    move.write(move_dict)

        return super(StockLandedCost, self).button_validate()

    def get_vals_from_invoice(self, invoice):
        """Get the cost line values from an invoice
        :param invoice: Invoice which you want to get the values from
        :type invoice: recordset
        :return: List of lines to create landed lines
        :rtype: [{}]"""
        company_currency = invoice.company_id.currency_id
        diff_currency = invoice.currency_id != company_currency
        if diff_currency:
            currency = invoice.currency_id.with_context(
                date=invoice.date_invoice)
        cost_lines = []
        for ail_brw in invoice.invoice_line_ids:
            if (not ail_brw.product_id or not
                    ail_brw.product_id.landed_cost_ok):
                continue
            price_subtotal = (
                currency.compute(ail_brw.price_subtotal,
                                 company_currency)
                if diff_currency else ail_brw.price_subtotal)
            cost_lines.append((0, 0, {
                'name': ail_brw.name,
                'account_id': ail_brw.account_id.id,
                'product_id': ail_brw.product_id.id,
                'price_unit': price_subtotal,
                'split_method': (
                    ail_brw.product_id.split_method or 'by_quantity'),
            }))
        return cost_lines

    @api.onchange('invoice_ids')
    def onchange_invoice_ids(self):
        for lc_brw in self:
            lc_brw.update({'cost_lines': [(5, 0, 0)]})
            cost_lines = []
            for inv_brw in lc_brw.invoice_ids:
                cost_lines += self.get_vals_from_invoice(inv_brw)
            lc_brw.update({'cost_lines': cost_lines})

    @api.multi
    def get_costs_from_invoices(self):
        """Update Costs Lines with Invoice Lines in the Invoices related to
        Document
        """
        for lc_brw in self:
            lc_brw.cost_lines.unlink()
            cost_lines = []
            for inv_brw in lc_brw.invoice_ids:
                cost_lines += self.get_vals_from_invoice(inv_brw)
            lc_brw.write({'cost_lines': cost_lines})
        return True

    @api.multi
    def get_valuation_lines(self):
        """It returns product valuations based on picking's moves
        """
        lines = []
        for move in (self.mapped('picking_ids').mapped('move_lines') +
                     self.move_ids):
            if (move.product_id.valuation != 'real_time' or
                    move.product_id.cost_method != 'fifo'):
                continue
            vals = {
                'product_id': move.product_id.id,
                'move_id': move.id,
                'quantity': move.product_qty,
                'former_cost': move.value,
                'weight': move.product_id.weight * move.product_qty,
                'volume': move.product_id.volume * move.product_qty
            }
            lines.append(vals)

        if not lines and self.mapped('picking_ids'):
            raise UserError(
                _('The selected picking does not contain any move that '
                  'would be impacted by landed costs. Landed costs are '
                  'only possible for products configured in real time '
                  'valuation with real price costing method. Please '
                  'make sure it is the case, or you selected the '
                  'correct picking'))
        return lines
