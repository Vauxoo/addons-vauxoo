# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Vauxoo
#    Author : Humberto Arocha <hbto@vauxoo.com>
#             Osval Reyes <osval@vauxoo.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
from openerp import api, models
from openerp.addons.product import _common
from openerp.tools import float_is_zero
_logger = logging.getLogger(__name__)
SEGMENTATION_COST = [
    'landed_cost',
    'subcontracting_cost',
    'material_cost',
    'production_cost',
]


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def update_material_cost_on_zero_segmentation(
            self, cr, uid, ids=None, context=None):
        prod_ids = self.search(cr, uid, [])
        counter = 0
        total = len(prod_ids)
        _logger.info('Cron Job will compute %s products', total)
        msglog = 'Computing cost for product: [%s]. %s/%s'
        res = []
        for prod_id in prod_ids:
            counter += 1
            _logger.info(msglog, str(prod_id), str(total), str(counter))
            rex = self._update_material_cost_on_zero_segmentation(
                cr, uid, prod_id, context=context)
            if rex:
                res.append(rex)
        total = len(res)
        counter = 0
        msglog = 'Computing cost for template: [%s]. %s/%s'
        for tmpl_id, std_price in res:
            counter += 1
            _logger.info(msglog, str(tmpl_id), str(total), str(counter))
            cr.execute('''
                UPDATE product_template
                SET material_cost = %(material_cost)s
                WHERE id = %(id)s
                       ''', {'material_cost': std_price, 'id': tmpl_id, })
        return True

    def _update_material_cost_on_zero_segmentation(
            self, cr, uid, ids, context=None):
        prod_brw = self.browse(cr, uid, ids)
        sum_sgmnt = sum(
            [getattr(prod_brw, fieldname)
             for fieldname in SEGMENTATION_COST])
        if not sum_sgmnt:
            return prod_brw.product_tmpl_id.id, prod_brw.standard_price
        return False


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _calc_price(
            self, cr, uid, bom, test=False, real_time_accounting=False,
            context=None):
        context = dict(context or {})
        price = 0
        uom_obj = self.pool.get("product.uom")
        tmpl_obj = self.pool.get('product.template')
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
                    cr, uid, product_id.uom_id.id,
                    prod_costs_dict[fieldname],
                    sbom.product_uom.id) * my_qty
                price += price_sgmnt
                sgmnt_dict[fieldname] += price_sgmnt

        if bom.routing_id:
            for wline in bom.routing_id.workcenter_lines:
                wc = wline.workcenter_id
                cycle = wline.cycle_nbr
                dd, mm = divmod(factor, wc.capacity_per_cycle)
                mult = (dd + (mm and 1.0 or 0.0))
                hour = float(
                    wline.hour_nbr * mult + (
                        (wc.time_start or 0.0) + (wc.time_stop or 0.0) +
                        cycle * (wc.time_cycle or 0.0)) * (
                            wc.time_efficiency or 1.0))
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
        product_tmpl_id = tmpl_obj.browse(
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
            tmpl_obj.write(
                cr, uid, [product_tmpl_id.id], {'standard_price': price},
                context=context)
        return self.ensure_change_price_log_messages(cr, uid, vals, ctx)

    @api.multi
    def _evaluate_threshold(self, bottom_th, computed_th, diff):
        """ Checks if bottom threshold is reached by computed threshold """
        precision_id = self.env['decimal.precision'].precision_get('Account')
        return float_is_zero(diff, precision_id) or\
            (self.standard_price and diff < 0 and
             computed_th > bottom_th)

    @staticmethod
    def _compute_threshold(std_price, new_price):
        """ Computes price variation used for threshold checking """
        return std_price and abs((new_price - std_price) * 100 / std_price)\
            or 0.0

    @api.multi
    def get_bottom_price_threshold(self):
        """ Returns bottom threshold giving priority to product's company,
        if not, user's company is taken """
        user = self.env['res.users'].browse(self._uid)
        threshold = self.company_id.\
            std_price_neg_threshold
        if not threshold:
            threshold = user.company_id.std_price_neg_threshold
        return threshold

    @api.model
    def ensure_change_price_log_messages(self, vals):
        """ Write in products (unless log_only is True) and then log messages
        if segments or products (or both) were updated """
        sgmnts_dict = vals.get('sgmnts_dict', False)
        log_only = vals.get('log_only', False)
        new_price = vals.get('new_price', False)
        prod_id = self.env.context.get('active_id')
        prod_model = self.env.context.get('active_model')
        product_id = self.env[prod_model].browse(prod_id)
        if prod_model == 'product.template':
            product_id = product_id.product_variant_ids
        if not product_id:
            return False
        if product_id.cost_method != 'standard':
            subject = 'I cowardly did not update cost.'
            body = 'Ignored Because product is not set as Standard'
            product_id.message_post(body=body, subject=subject)
            return False

        # Just writting segments to be consistent with segmentation
        # feature. TODO: A report should show differences.
        body = ''
        subject = "Segments NOT updated. "
        if sgmnts_dict:
            if not log_only:
                product_id.write(sgmnts_dict)
            subject = "Segments updated. "
            body = 'Segments were written CHECK AFTERWARDS.'\
                '%s' % str(sgmnts_dict)

        if not vals.get('threshold_reached', False):
            if not log_only:
                product_id.write(new_price)
            subject += "Cost updated correctly. "
            body += ""
        else:
            subject += 'I cowardly did not update cost, Standard new\n'
            body += "Price is %(comp_th).2f%% less than old price\n"\
                "new %(new)s old %(old)s \n"\
                "(current max allowed is %(max_th)s)\n" % dict(
                    old=vals['current_price'],
                    new=new_price['standard_price'],
                    comp_th=vals['computed_th'],
                    max_th=vals['current_bottom_th'])
        product_id.message_post(body=body, subject=subject)
        return new_price['standard_price']

    def compute_price(self, cr, uid, product_ids, template_ids=False,
                      recursive=False, test=False, real_time_accounting=False,
                      context=None):
        """Will return test dict when the test = False
        Multiple ids at once?
        testdict is used to inform the user about the changes to be made
        """
        context = dict(context or {})
        if '_calc_price_recursive' not in context:
            context['_calc_price_recursive'] = recursive
        bom_obj = self.pool.get('mrp.bom')
        prod_obj = self.pool.get('product.product')
        testdict = {}
        real_time = real_time_accounting
        ids = template_ids
        model = 'product.template'
        if product_ids:
            ids = product_ids
            model = 'product.product'

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

        for prod_id in ids:
            bom_id = _bom_find(prod_id)
            if not bom_id:
                continue
            # In recursive mode, it will first compute the prices of child
            # boms
            if recursive and not test:
                # Search the products that are components of this bom of
                # prod_id
                bom = bom_obj.browse(cr, uid, bom_id, context=context)

                # Call compute_price on these subproducts
                prod_set = set([x.product_id.id for x in bom.bom_line_ids])
                self.compute_price(
                    cr, uid, product_ids=list(prod_set), template_ids=[],
                    recursive=recursive, test=test,
                    real_time_accounting=real_time, context=context)

            # Use calc price to calculate and put the price on the product
            # of the BoM if necessary
            price = self._calc_price(
                cr, uid, bom_obj.browse(cr, uid, bom_id, context=context),
                test=test, real_time_accounting=real_time, context=context)
            if test:
                testdict.update({prod_id: price})
        if test:
            return testdict
        return True

    @api.multi
    def do_change_standard_price(self, new_price):
        """ When updating the standard_price for a product using the wizard, it
        checks if bottom threshold got reached, if not let it get updated and
        post messages about it
        """
        bottom_th = self.get_bottom_price_threshold()
        diff = new_price - self.standard_price
        computed_th = self._compute_threshold(self.standard_price, new_price)
        threshold_reached = self._evaluate_threshold(bottom_th,
                                                     computed_th, diff)
        vals = {
            'log_only': True,
            'new_price': {'standard_price': new_price},
            'current_price': self.standard_price,
            'threshold_reached': threshold_reached,
            'computed_th': computed_th,
            'current_bottom_th': bottom_th,
        }
        self.ensure_change_price_log_messages(vals)
        if threshold_reached:
            return True
        res = super(ProductTemplate, self).do_change_standard_price(
            new_price)
        return res
