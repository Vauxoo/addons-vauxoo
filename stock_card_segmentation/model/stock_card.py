# coding: utf-8

from __future__ import division
from openerp import models, fields
import openerp.addons.decimal_precision as dp
SEGMENTATION = ['material', 'landed', 'production', 'subcontracting']


class StockCardProduct(models.TransientModel):
    _inherit = ['stock.card.product']

    def _get_fieldnames(self):
        res = super(StockCardProduct, self)._get_fieldnames()
        res.update({
            'material': 'material_cost',
            'landed': 'landed_cost',
            'production': 'production_cost',
            'subcontracting': 'subcontracting_cost',
        })
        return res

    def _get_avg_fields(self):
        res = super(StockCardProduct, self)._get_avg_fields()
        return res + SEGMENTATION

    def _get_quant_values(self, move_id, col='', inner='', where=''):

        col = ['%s_cost' % sgmnt for sgmnt in SEGMENTATION]
        col = ['COALESCE(%s, 0.0) AS %s' % (cl, cl) for cl in col]
        col = ', ' + ', '.join(col)
        return super(StockCardProduct, self)._get_quant_values(
            move_id=move_id, col=col, inner=inner, where=where)

    def _get_stock_card_move_line_dict(self, row, vals):
        res = super(StockCardProduct, self)._get_stock_card_move_line_dict(
            row, vals)
        res = dict(
            res,
            material=vals['material'],
            landed=vals['landed'],
            production=vals['production'],
            subcontracting=vals['subcontracting'],
            material_valuation=vals['material_valuation'],
            landed_valuation=vals['landed_valuation'],
            production_valuation=vals['production_valuation'],
            subcontracting_valuation=vals['subcontracting_valuation'],
        )
        return res

    def _get_default_params(self, product_id, locations_ids=None):
        res = super(StockCardProduct, self)._get_default_params(
            product_id, locations_ids)
        res.update({}.fromkeys(SEGMENTATION, 0.0))
        res.update({}.fromkeys(
            ['%s_total' % sgmnt for sgmnt in SEGMENTATION], 0.0))
        res.update({}.fromkeys(
            ['%s_valuation' % sgmnt for sgmnt in SEGMENTATION], 0.0))
        res.update({}.fromkeys(
            ['%s_accum_var' % sgmnt for sgmnt in SEGMENTATION], 0.0))
        res.update({}.fromkeys(
            ['prior_val_%s' % sgmnt for sgmnt in SEGMENTATION], 0.0))
        res.update({}.fromkeys(
            ['previous_val_%s' % sgmnt for sgmnt in SEGMENTATION], 0.0))
        res.update({}.fromkeys(
            ['prior_avg_%s' % sgmnt for sgmnt in SEGMENTATION], 0.0))
        return res

    def _get_price_on_consumed(self, row, vals, qntval):
        move_id = row['move_id']
        product_qty = vals['product_qty']
        delta_qty = vals['direction'] * row['product_qty']
        final_qty = product_qty + delta_qty
        vals['product_qty'] += (vals['direction'] * row['product_qty'])

        if not vals['move_dict'].get(move_id):
            vals['move_dict'][move_id] = {}

        vals['move_dict'][move_id]['average'] = vals['average']
        for sgmnt in SEGMENTATION:
            vals['move_dict'][move_id][sgmnt] = vals[sgmnt]

        antiquant = any([qnt['antiquant'] for qnt in qntval])
        if final_qty < 0 and antiquant:
            vals['move_dict'][move_id]['average'] = vals['average']
            vals['move_valuation'] = sum(
                [vals['average'] * qnt['qty'] for qnt in qntval
                 if qnt['qty'] > 0])
            for sgmnt in SEGMENTATION:
                vals['move_dict'][move_id][sgmnt] = vals[sgmnt]
                vals['%s_valuation' % sgmnt] = sum(
                    [vals[sgmnt] * qnt['qty'] for qnt in qntval
                     if qnt['qty'] > 0])
            return True

        vals['move_valuation'] = 0.0
        for sgmnt in SEGMENTATION:
            vals['%s_valuation' % sgmnt] = 0.0
        self._get_price_on_consumed_quant_iter(product_qty, row, vals, qntval)
        return True

    def _get_price_on_consumed_quant_iter(
            self, product_qty, row, vals, qntval):
        for qnt in qntval:
            if qnt['qty'] < 0:
                continue

            prior_qty = product_qty

            if product_qty > 0:
                self._get_price_on_consumed_quant_pstv(
                    product_qty, prior_qty, vals, qnt)
            else:  # product_qty < 0
                self._get_price_on_consumed_quant_ngtv(product_qty, vals, qnt)
            product_qty += vals['direction'] * qnt['qty']

        return True

    def _get_price_on_consumed_quant_pstv(
            self, product_qty, prior_qty, vals, qnt):
        if product_qty + vals['direction'] * qnt['qty'] >= 0:
            if not vals['rewind']:
                vals['move_valuation'] += vals['average'] * qnt['qty']
                for sgmnt in SEGMENTATION:
                    vals['%s_valuation' % sgmnt] += \
                        vals[sgmnt] * qnt['qty']
            else:
                vals['move_valuation'] += \
                    vals['prior_average'] * qnt['qty']
                for sgmnt in SEGMENTATION:
                    vals['%s_valuation' % sgmnt] += \
                        vals['prior_avg_%s' % sgmnt] * qnt['qty']
        else:  # product_qty + qnt < 0
            if not vals['rewind']:
                vals['move_valuation'] += vals['average'] * qnt['qty']
                for sgmnt in SEGMENTATION:
                    vals['%s_valuation' % sgmnt] += \
                        vals[sgmnt] * qnt['qty']
            else:  # rewind
                residual = qnt['qty'] - product_qty

                vals['move_valuation'] += (
                    vals['prior_average'] * prior_qty +
                    vals['future_average'] * residual)
                for sgmnt in SEGMENTATION:
                    vals['%s_valuation' % sgmnt] += (
                        vals['prior_avg_%s' % sgmnt] * prior_qty +
                        vals['future_%s' % sgmnt] * residual)

        return True

    def _get_price_on_consumed_quant_ngtv(
            self, product_qty, vals, qnt):
        if not vals['rewind']:
            vals['move_valuation'] += vals['average'] * qnt['qty']
            for sgmnt in SEGMENTATION:
                vals['%s_valuation' % sgmnt] += \
                    vals[sgmnt] * qnt['qty']
        else:
            vals['move_valuation'] += \
                vals['future_average'] * qnt['qty']
            for sgmnt in SEGMENTATION:
                vals['%s_valuation' % sgmnt] += \
                    vals['future_%s' % sgmnt] * qnt['qty']

        return True

    def _get_price_on_supplier_return(self, row, vals, qntval):
        vals['product_qty'] += (vals['direction'] * row['product_qty'])
        sm_obj = self.env['stock.move']
        move_id = sm_obj.browse(row['move_id'])
        # Cost is the one record in the stock_move, cost in the
        # quant record includes other segmentation cost: landed_cost,
        # material_cost, production_cost, subcontracting_cost
        # Inventory Value has to be decreased by the amount of purchase
        # TODO: BEWARE price_unit needs to be normalised
        origin_id = move_id.origin_returned_move_id
        current_quants = set(move_id.quant_ids.ids)
        origin_quants = set(origin_id.quant_ids.ids)
        quants_exists = current_quants.issubset(origin_quants)
        if quants_exists:
            vals['move_valuation'] = sum(
                [qnt['cost'] * qnt['qty'] for qnt in qntval])
        # / ! \ This is missing when current move's quants are partially
        # located in origin's quants, so it's taking average cost temporarily
        else:
            vals['move_valuation'] = sum(
                [vals['average'] * qnt['qty'] for qnt in qntval])
        for sgmnt in SEGMENTATION:
            vals['%s_valuation' % sgmnt] = sum(
                [qnt['%s_cost' % sgmnt] * qnt['qty'] for qnt in qntval])

        return True

    def _get_price_on_supplied(self, row, vals, qntval):
        vals['product_qty'] += (vals['direction'] * row['product_qty'])
        vals['move_valuation'] = sum(
            [qnt['cost'] * qnt['qty'] for qnt in qntval])

        for sgmnt in SEGMENTATION:
            vals['%s_valuation' % sgmnt] = sum(
                [qnt['%s_cost' % sgmnt] * qnt['qty'] for qnt in qntval])

        return True

    def _get_price_on_customer_return(self, row, vals, qntval):
        vals['product_qty'] += (vals['direction'] * row['product_qty'])
        sm_obj = self.env['stock.move']
        move_id = row['move_id']
        move_brw = sm_obj.browse(move_id)
        origin_id = move_brw.origin_returned_move_id or move_brw.move_dest_id
        origin_id = origin_id.id

        if vals.get('global_val') and not origin_id:
            # /!\ NOTE: There is no origin and this Conditional Statement
            # applies only on Stock Card per Warehouse. We will fall-back for
            # the value in the Global Stock Card thus copying original values
            vals['move_valuation'] = \
                vals['global_val'][move_id]['move_valuation']

            for sgmnt in SEGMENTATION:
                vals['%s_valuation' % sgmnt] = \
                    vals['global_val'][move_id]['%s_valuation' % sgmnt]
            return True

        old_average = (
            vals.get('global_val') and
            vals['global_val'].get(origin_id) and
            vals['global_val'][origin_id]['average'] or
            vals['move_dict'].get(origin_id) and
            vals['move_dict'][origin_id]['average'] or vals['average'])
        # /!\ NOTE: Normalize this computation
        vals['move_valuation'] = sum(
            [old_average * qnt['qty'] for qnt in qntval] +
            [dquant.cost * move_brw.product_qty
             for dquant in move_brw.discrete_ids])

        for sgmnt in SEGMENTATION:
            old_average = (
                vals.get('global_val') and
                vals['global_val'].get(origin_id) and
                vals['global_val'][origin_id][sgmnt] or
                vals['move_dict'].get(origin_id) and
                vals['move_dict'][origin_id][sgmnt] or vals[sgmnt])

            vals['%s_valuation' % sgmnt] = sum(
                [old_average * qnt['qty'] for qnt in qntval] +
                [dquant.cost * move_brw.product_qty
                 for dquant in move_brw.discrete_ids
                 if dquant.segmentation_cost == '%s_cost' % sgmnt])

        return True

    def _get_move_average(self, row, vals):
        qty = row['product_qty']
        vals['cost_unit'] = vals['move_valuation'] / qty if qty else 0.0
        for sgmnt in SEGMENTATION:
            vals['%s_unit' % sgmnt] = vals['%s_valuation' %
                                           sgmnt] / qty if qty else 0.0

        vals['inventory_valuation'] += (
            vals['direction'] * vals['move_valuation'])
        for sgmnt in SEGMENTATION:
            vals['%s_total' % sgmnt] += (
                vals['direction'] * vals['%s_valuation' % sgmnt])

        if vals['previous_qty'] < 0 and vals['direction'] > 0:
            vals['accumulated_variation'] += vals['move_valuation']
            vals['accumulated_qty'] += row['product_qty']
            for sgmnt in SEGMENTATION:
                vals['%s_accum_var' % sgmnt] += vals['%s_valuation' % sgmnt]

            vals['average'] = (
                vals['accumulated_variation'] / vals['accumulated_qty'] if
                vals['accumulated_qty'] else vals['average'])

            for sgmnt in SEGMENTATION:
                vals[sgmnt] = (
                    vals['%s_accum_var' % sgmnt] / vals['accumulated_qty'] if
                    vals['accumulated_qty'] else vals[sgmnt])

            if vals['product_qty'] >= 0:
                vals['accumulated_variation'] = 0.0
                vals['accumulated_qty'] = 0.0
                for sgmnt in SEGMENTATION:
                    vals['%s_accum_var' % sgmnt] = 0.0
        else:
            vals['average'] = (
                vals['inventory_valuation'] / vals['product_qty'] if
                vals['product_qty'] else vals['average'])
            for sgmnt in SEGMENTATION:
                vals[sgmnt] = (
                    vals['%s_total' % sgmnt] / vals['product_qty'] if
                    vals['product_qty'] else vals[sgmnt])
        return True

    def _pre_get_average_by_move(self, row, vals):
        vals['previous_qty'] = vals['product_qty']
        vals['previous_valuation'] = vals['inventory_valuation']
        vals['previous_average'] = vals['average']
        for sgmnt in SEGMENTATION:
            vals['previous_val_%s' % sgmnt] = vals['%s_total' % sgmnt]
            vals['previous_avg%s' % sgmnt] = vals[sgmnt]
        return True

    def _post_get_average_by_move(self, row, vals):
        if not vals['rewind']:
            if vals['previous_qty'] > 0 and vals['product_qty'] < 0:
                vals['prior_qty'] = vals['previous_qty']
                vals['prior_valuation'] = vals['previous_valuation']
                vals['prior_average'] = vals['previous_average']

                for sgmnt in SEGMENTATION:
                    vals['prior_val_%s' % sgmnt] = \
                        vals['previous_val_%s' % sgmnt]
                    vals['prior_avg_%s' % sgmnt] = \
                        vals['previous_avg%s' % sgmnt]

            if vals['product_qty'] < 0 and vals['direction'] < 0:
                vals['accumulated_move'].append(row)
            elif vals['previous_qty'] < 0 and vals['direction'] > 0:
                vals['accumulated_move'].append(row)
                vals['rewind'] = True
                vals['old_queue'] = vals['queue'][:]
                vals['queue'] = vals['accumulated_move'][:]

                vals['product_qty'] = vals['prior_qty']
                vals['inventory_valuation'] = vals['prior_valuation']
                vals['future_average'] = vals['average']

                for sgmnt in SEGMENTATION:
                    vals['%s_total' % sgmnt] = \
                        vals['prior_val_%s' % sgmnt]
                    vals['future_%s' % sgmnt] = vals[sgmnt]

                vals['accumulated_variation'] = 0.0
                vals['accumulated_qty'] = 0.0
                for sgmnt in SEGMENTATION:
                    vals['%s_accum_var' % sgmnt] = 0.0

        else:
            if not vals['queue']:
                vals['rewind'] = False
                vals['queue'] = vals['old_queue'][:]

            if vals['product_qty'] > 0:
                vals['accumulated_move'] = []
        return True


class StockCardMove(models.TransientModel):
    _inherit = 'stock.card.move'
    material = fields.Float(
        string='Material Cost',
        digits=dp.get_precision('Account'),
        readonly=True)
    landed = fields.Float(
        string='Landed Cost',
        digits=dp.get_precision('Account'),
        readonly=True)
    production = fields.Float(
        string='Production Cost',
        digits=dp.get_precision('Account'),
        readonly=True)
    subcontracting = fields.Float(
        string='Subcontracting Cost',
        digits=dp.get_precision('Account'),
        readonly=True)
