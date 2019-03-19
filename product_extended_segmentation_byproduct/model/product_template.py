# -*- coding: utf-8 -*-
from __future__ import division

from openerp import models
from openerp.addons.product import _common
SEGMENTATION_COST = [
    'landed_cost',
    'subcontracting_cost',
    'material_cost',
    'production_cost',
]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _calc_price(
            self, cr, uid, bom, test=False, real_time_accounting=False,
            context=None):
        if not bom.sub_products:
            super(ProductTemplate, self)._calc_price(
                cr, uid, bom, test, real_time_accounting, context)
        context = dict(context or {})
        price = 0
        uom_obj = self.pool.get("product.uom")
        wizard_obj = self.pool.get("stock.change.standard.price")
        bom_obj = self.pool.get('mrp.bom')
        prod_obj = self.pool.get('product.product')
        model = 'product.product'

        def _get_sgmnt(prod_id):
            res = {}
            sum_sgmnt = 0.0
            for fieldname in SEGMENTATION_COST:
                fn_cost = getattr(prod_id, fieldname)
                sum_sgmnt += fn_cost
                res[fieldname] = fn_cost
            if not sum_sgmnt:
                res['material_cost'] = prod_id.standard_price
            return res

        def _bom_find(prod_id):
            if model == 'product.product':
                # if not look for template
                bom_id = bom_obj._bom_find(
                    cr, uid, product_id=prod_id, context=context)
                if bom_id:
                    return bom_id
                prod_id = prod_obj.browse(
                    cr, uid, prod_id, context=context).product_tmpl_id.id
            return bom_obj._bom_find(
                cr, uid, product_tmpl_id=prod_id, context=context)

        def _factor(factor, product_efficiency, product_rounding):
            factor = factor / (product_efficiency or 1.0)
            factor = _common.ceiling(factor, product_rounding)
            if factor < product_rounding:
                factor = product_rounding
            return factor

        factor = _factor(1.0, bom.product_efficiency, bom.product_rounding)

        sgmnt_dict = {}.fromkeys(SEGMENTATION_COST, 0.0)
        for sbom in bom.bom_line_ids:
            my_qty = sbom.product_qty / sbom.product_efficiency
            if sbom.attribute_value_ids:
                continue
            # No attribute_value_ids means the bom line is not variant
            # specific

            prod_costs_dict = {}.fromkeys(SEGMENTATION_COST, 0.0)
            product_id = sbom.product_id
            if product_id.cost_method == 'average':
                prod_costs_dict = _get_sgmnt(product_id)
            else:
                #  NOTE: Case when product is REAL or STANDARD
                if test and context['_calc_price_recursive']:
                    init_bom_id = _bom_find(product_id.id)
                    if init_bom_id:
                        prod_costs_dict['material_cost'] = self._calc_price(
                            cr, uid, bom_obj.browse(
                                cr, uid, init_bom_id, context=context),
                            test=test,
                            real_time_accounting=real_time_accounting,
                            context=context)
                    else:
                        prod_costs_dict = _get_sgmnt(product_id)
                else:
                    prod_costs_dict = _get_sgmnt(product_id)

            for fieldname in SEGMENTATION_COST:
                # NOTE: Is this price well Normalized
                if not prod_costs_dict[fieldname]:
                    continue
                price_sgmnt = uom_obj._compute_price(
                    cr, uid, product_id.uom_id.id, prod_costs_dict[fieldname],
                    sbom.product_uom.id) * my_qty
                price += price_sgmnt
                sgmnt_dict[fieldname] += price_sgmnt

        for sub_prod in bom.sub_products:
            prod_costs_dict = {}.fromkeys(SEGMENTATION_COST, 0.0)
            product_id = sub_prod.product_id
            if product_id.cost_method == 'average':
                prod_costs_dict = _get_sgmnt(product_id)
            else:
                #  NOTE: Case when product is REAL or STANDARD
                if test and context['_calc_price_recursive']:
                    init_bom_id = _bom_find(product_id.id)
                    if init_bom_id:
                        prod_costs_dict['material_cost'] = self._calc_price(
                            cr, uid, bom_obj.browse(
                                cr, uid, init_bom_id, context=context),
                            test=test,
                            real_time_accounting=real_time_accounting,
                            context=context)
                    else:
                        prod_costs_dict = _get_sgmnt(product_id)
                else:
                    prod_costs_dict = _get_sgmnt(product_id)

            for fieldname in SEGMENTATION_COST:
                # NOTE: Is this price well Normalized
                if not prod_costs_dict[fieldname]:
                    continue
                price_sgmnt = uom_obj._compute_price(
                    cr, uid, product_id.uom_id.id, prod_costs_dict[fieldname],
                    sub_prod.product_uom.id) * sub_prod.product_qty
                price -= price_sgmnt
                sgmnt_dict[fieldname] -= price_sgmnt

        if bom.routing_id:
            for wline in bom.routing_id.workcenter_lines:
                wc = wline.workcenter_id
                cycle = wline.cycle_nbr
                dd, mm = divmod(factor, wc.capacity_per_cycle)
                mult = (dd + (mm and 1.0 or 0.0))
                hour = float(wline.hour_nbr * mult + (
                    (wc.time_start or 0.0) + (wc.time_stop or 0.0) + cycle * (
                        wc.time_cycle or 0.0)) * (wc.time_efficiency or 1.0))
                routing_price = wc.costs_cycle * cycle + wc.costs_hour * hour
                routing_price = uom_obj._compute_price(
                    cr, uid, bom.product_uom.id, routing_price,
                    bom.product_id.uom_id.id)
                price += routing_price
                # /!\ NOTE: If not segmentation set on WC fallback to
                # production_cost segmentation
                fn = wc.segmentation_cost or 'production_cost'
                sgmnt_dict[fn] += routing_price

        # Convert on product UoM quantities
        if price > 0:
            price = uom_obj._compute_price(
                cr, uid, bom.product_uom.id, price / bom.product_qty,
                bom.product_id.uom_id.id)

        if test:
            return price

        # NOTE: Instanciating BOM related product
        product_tmpl_id = self.browse(
            cr, uid, bom.product_tmpl_id.id, context=context)

        bottom_th = product_tmpl_id.get_bottom_price_threshold()

        current_price = product_tmpl_id.standard_price
        diff = price - current_price
        computed_th = self._compute_threshold(current_price, price)

        if diff < 0 and current_price == 0:
            return price

        threshold_reached = product_tmpl_id._evaluate_threshold(
            bottom_th, computed_th, diff)
        vals = {
            'threshold_reached': threshold_reached,
            'sgmnts_dict': sgmnt_dict,
            'new_price': {'standard_price': price},
            'current_price': current_price,
            'computed_th': computed_th,
            'current_bottom_th': bottom_th,
        }

        ctx = dict(context or {})
        ctx.update({
            'active_id': product_tmpl_id.id,
            'active_ids': product_tmpl_id.ids,
            'active_model': product_tmpl_id._name,
        })
        if threshold_reached:
            return self.ensure_change_price_log_messages(cr, uid, vals, ctx)

        diff = product_tmpl_id.standard_price - price
        # Write standard price
        if product_tmpl_id.valuation == "real_time" and \
                real_time_accounting and diff:
            # Call wizard function here
            wizard_id = wizard_obj.create(
                cr, uid, {'new_price': price}, context=ctx)
            wizard_obj.change_price(cr, uid, [wizard_id], context=ctx)
        else:
            self.write(cr, uid, [product_tmpl_id.id],
                       {'standard_price': price}, context=context)
        return self.ensure_change_price_log_messages(cr, uid, vals, ctx)
