# coding: utf-8

from openerp import models
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
        context = dict(context or {})
        price = 0
        uom_obj = self.pool.get("product.uom")
        quant_obj = self.pool.get("stock.quant")
        tmpl_obj = self.pool.get('product.template')

        def quant_search(product_id):
            ARGS = [('product_id', '=', product_id)]
            return quant_obj.search(
                cr, uid, ARGS, order='in_date DESC', limit=1)

        for sbom in bom.bom_line_ids:
            my_qty = sbom.product_qty / sbom.product_efficiency
            if sbom.attribute_value_ids:
                continue
            # No attribute_value_ids means the bom line is not variant
            # specific

            # NOTE: find for this product last quant available and cycle
            # over ll the segmentation costs
            quant = quant_search(sbom.product_id.id)
            if not quant:
                price += uom_obj._compute_price(
                    cr, uid, sbom.product_id.uom_id.id,
                    sbom.product_id.standard_price,
                    sbom.product_uom.id) * my_qty

            quant_brw = quant_obj.browse(cr, uid, quant[0], context=context)
            for fieldname in SEGMENTATION_COST:
                # TODO: Is this price well Normalized
                price += uom_obj._compute_price(
                    cr, uid, sbom.product_id.uom_id.id,
                    getattr(quant_brw, fieldname),
                    sbom.product_uom.id) * my_qty

        if bom.routing_id:
            for wline in bom.routing_id.workcenter_lines:
                wc = wline.workcenter_id
                cycle = wline.cycle_nbr
                hour = \
                    (wc.time_start + wc.time_stop + cycle * wc.time_cycle) * \
                    (wc.time_efficiency or 1.0)
                price += wc.costs_cycle * cycle + wc.costs_hour * hour
                price = uom_obj._compute_price(
                    cr, uid, bom.product_uom.id, price,
                    bom.product_id.uom_id.id)

        # Convert on product UoM quantities
        if price > 0:
            price = uom_obj._compute_price(
                cr, uid, bom.product_uom.id, price / bom.product_qty,
                bom.product_id.uom_id.id)

        product = tmpl_obj.browse(
            cr, uid, bom.product_tmpl_id.id, context=context)
        if not test:
            if (product.valuation != "real_time" or not real_time_accounting):
                tmpl_obj.write(
                    cr, uid, [product.id], {'standard_price': price},
                    context=context)
            else:
                # Call wizard function here
                wizard_obj = self.pool.get("stock.change.standard.price")
                ctx = context.copy()
                ctx.update(
                    {'active_id': product.id,
                     'active_model': 'product.template'})
                wiz_id = wizard_obj.create(
                    cr, uid, {'new_price': price}, context=ctx)
                wizard_obj.change_price(cr, uid, [wiz_id], context=ctx)
        return price
