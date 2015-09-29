# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp import models, fields, api, _
from pprint import pprint


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
            raise osv.except_osv(
                _('Error!'),
                _('The selected picking does not contain any move that would '
                  'be impacted by landed costs. Landed costs are only possible'
                  ' for products configured in real time valuation with real'
                  ' price or average costing method. Please make sure it is '
                  'the case, or you selected the correct picking'))
        return lines

    @api.multi
    def compute_average_cost(self):
        '''
        This method updates standard_price field in products with costing
        method equal to average
        '''
        product_obj = self.env['product.product']

        for cost in self:
            prod_qty_dict = {}
            prod_val_dict = {}
            prod_adj_dict = {}
            for line in cost.valuation_adjustment_lines:
                if not line.move_id:
                    continue

                if line.move_id.product_id.cost_method != 'average':
                    continue

                # Current quantity of products available
                if not prod_qty_dict.get(line.move_id.product_id.id):
                    prod_qty_dict[line.move_id.product_id.id] = \
                        line.move_id.product_id.product_tmpl_id.qty_available

                # Current valuation of products available
                if not prod_val_dict.get(line.move_id.product_id.id):
                    prod_val_dict[line.move_id.product_id.id] = \
                        line.move_id.product_id.standard_price * \
                        line.move_id.product_id.product_tmpl_id.qty_available

                # Current Landed Value for product
                if not prod_adj_dict.get(line.move_id.product_id.id):
                    prod_adj_dict[line.move_id.product_id.id] = \
                        line.additional_landed_cost
                else:
                    prod_adj_dict[line.move_id.product_id.id] += \
                        line.additional_landed_cost

            for k in prod_qty_dict.keys():
                if prod_qty_dict[k] < 0:
                    prod = product_obj.browse(k)
                    raise Warning(
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
        super(StockLandedCost, self).button_validate()
        self.compute_average_cost()
        return True
