# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo.tools.float_utils import float_is_zero
from odoo import models, _, api, tools, fields
_logger = logging.getLogger(__name__)

SEGMENTATION_COST = [
    'landed_cost',
    'subcontracting_cost',
    'material_cost',
    'production_cost',
]


class Product(models.Model):

    _inherit = "product.product"

    @api.multi
    def update_material_cost_on_zero_segmentation(self):
        prod_ids = self.search([])
        counter = 0
        total = len(prod_ids)
        _logger.info('Cron Job will compute %s products', total)
        msglog = 'Computing cost for product: [%s]. %s/%s'
        res = []
        for prod_id in prod_ids:
            counter += 1
            _logger.info(msglog, str(prod_id), str(total), str(counter))
            rex = prod_id._update_material_cost_on_zero_segmentation()
            if rex:
                res.append(rex)
        total = len(res)
        counter = 0
        msglog = 'Computing cost for template: [%s]. %s/%s'
        for tmpl_id, std_price in res:
            counter += 1
            _logger.info(msglog, str(tmpl_id), str(total), str(counter))
            self.env.cr.execute('''
                UPDATE product_template
                SET material_cost = {material_cost}
                WHERE id = {id}
                    '''.format(
                material_cost=std_price,
                id=tmpl_id,
            ))
        return True

    @api.multi
    def _update_material_cost_on_zero_segmentation(self):
        prod_brw = self
        sum_sgmnt = sum(
            [getattr(prod_brw, fieldname)
             for fieldname in SEGMENTATION_COST])
        if not sum_sgmnt:
            return prod_brw.product_tmpl_id.id, prod_brw.standard_price
        return False

    @api.multi
    def compute_segmetation_price(self, cron=None, wizard=None):
        bom_obj = self.env['mrp.bom']
        for product in self:
            bom = bom_obj._bom_find(product=product)
            if bom:
                try:
                    product._calc_price_seg(bom, wizard=wizard)
                except BaseException as error:
                    _logger.error(error)
                    product.message_post(
                        body=_('Error at the moment to '
                               'update the standard price'),
                        subject=error)
        if not cron:
            self.clear_caches()
        return True

    @api.multi
    def compute_price(self):
        bom_obj = self.env['mrp.bom']
        action_rec = self.env.ref(
            'stock_account.action_view_change_standard_price')
        for product in self:
            bom = bom_obj._bom_find(product=product)
            if bom:
                price = product._calc_price_seg(bom, True)['price']
                if action_rec:
                    action = action_rec.read([])[0]
                    action['context'] = {'default_new_price': price}
                    return action
        return True

    @staticmethod
    def _compute_threshold(std_price, new_price):
        """ Computes price variation used for threshold checking """
        return std_price and abs((new_price - std_price) * 100 / std_price)

    @api.multi
    def ensure_change_price_log_messages(self, vals):
        """ Write in products (unless log_only is True) and then log messages
        if segments or products (or both) were updated """
        sgmnts_dict = vals.get('sgmnts_dict', False)
        log_only = vals.get('log_only', False)
        new_price = vals.get('new_price', False)
        # Just writting segments to be consistent with segmentation
        # feature. TODO: A report should show differences.
        body = ''
        subject = "Segments NOT updated. "
        if sgmnts_dict and not log_only:
            subject = "Segments updated. "
            body = 'Segments were written CHECK AFTERWARDS.'\
                '{0}'.format(str(sgmnts_dict))

        if not vals.get('threshold_reached', False):
            subject += "Cost updated correctly. "
            body += ""
        else:
            subject += 'I cowardly did not update cost, Standard new\n'
            body += "Price is {comp_th:.2f}% less than old price\n"\
                "new {new} old {old} \n"\
                "(current max allowed is {max_th})\n"\
                .format(old=vals['current_price'],
                        new=new_price['standard_price'],
                        comp_th=vals['computed_th'],
                        max_th=vals['current_bottom_th'])
        self.message_post(body=body, subject=subject)
        return new_price['standard_price']

    @tools.ormcache('bom', 'internal')
    def _calc_price_seg(self, bom, internal=None, wizard=None):
        """Computing the standard price from BOM recursively with its segmentations
        :param bom: Bom which you want to compute the cost
        :type bom: mrp.bom()
        :param internal: Used to return the new cost without writing the cost
        to the target product
        :param wizard: Used to write new cost even if is internal when function
        called from the wizard
        :return: The new price
        :rtype: str"""
        price = 0.0
        result, result2 = bom.explode(self, 1)

        def _get_sgmnt(prod_id):
            res = {}
            sum_sgmnt = 0.0
            candidates = prod_id._get_fifo_candidates_in_move()
            prod_id = candidates[0] if candidates else prod_id
            for fieldname in SEGMENTATION_COST:
                fn_cost = getattr(prod_id, fieldname)
                sum_sgmnt += fn_cost
                res[fieldname] = fn_cost
            if not sum_sgmnt:
                res['material_cost'] = (
                    prod_id.standard_price
                    if hasattr(prod_id, 'standard_price')
                    else prod_id.price_unit)
            return res

        sgmnt_dict = {}.fromkeys(SEGMENTATION_COST, 0.0)
        for sbom, sbom_data in result2:
            product_id = sbom.product_id
            prod_costs_dict = _get_sgmnt(product_id)
            child_bom_id = sbom.child_bom_id
            if child_bom_id and not product_id.cost_method == 'average':
                prod_costs_dict = self._calc_price_seg(
                    child_bom_id, True, wizard)

            for fieldname in SEGMENTATION_COST:
                # NOTE: Is this price well Normalized
                if not prod_costs_dict[fieldname]:
                    continue
                price_sgmnt = product_id.uom_id._compute_price(
                    prod_costs_dict[fieldname],
                    sbom.product_uom_id) * sbom_data['qty']
                price += price_sgmnt
                sgmnt_dict[fieldname] += price_sgmnt

        total_cost = 0.0
        for order in bom.routing_id.operation_ids or ():
            workcenter = order.workcenter_id
            routing_price = (order.time_cycle / 60) * workcenter.costs_hour
            routing_price = bom.product_uom_id._compute_price(
                routing_price, bom.product_id.uom_id)
            fn = workcenter.segmentation_cost or 'production_cost'
            sgmnt_dict[fn] += routing_price
            total_cost += routing_price

        price += total_cost
        # Convert on product UoM quantities
        if price > 0:
            price = bom.product_uom_id._compute_price(
                price / bom.product_qty, self.uom_id)
        if internal and not wizard:
            sgmnt_dict['price'] = price
            return sgmnt_dict

        product_tmpl_id = bom.product_tmpl_id

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

        if threshold_reached:
            sgmnt_dict['standard_price'] = price
            self.ensure_change_price_log_messages(vals)
            return price

        diff = product_tmpl_id.standard_price - price
        if product_tmpl_id.valuation == "real_time" and diff:
            # Call wizard function here
            wizard_id = self.create_change_standard_price_wizard(price)
            wizard_id.change_price()
            self.write(sgmnt_dict)
            self.ensure_change_price_log_messages(vals)
            return price

        sgmnt_dict['standard_price'] = price
        self.write(sgmnt_dict)
        self.ensure_change_price_log_messages(vals)
        return price

    def create_change_standard_price_wizard(self, price):
        wizard_obj = self.env["stock.change.standard.price"]
        wizard_id = wizard_obj.with_context(
            {'active_model': 'product.product',
             'active_id': self.id,
             'active_ids': self.ids}).create(
            {'new_price': price,
             'counterpart_account_id':
             self.property_account_expense_id.id or
             self.categ_id.property_account_expense_categ_id.id,
             'counterpart_account_id_required': True})
        return wizard_id

    def _calc_price(self, bom, segmentation=False):
        """Computing cost from bom recursively"""
        if segmentation:
            return self._calc_price_seg(bom)

        return super(Product, self)._calc_price(bom)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def get_bottom_price_threshold(self):
        """ Returns bottom threshold giving priority to product's company,
        if not, user's company is taken """
        threshold = self.company_id.std_price_neg_threshold
        if not threshold:
            threshold = self.env.user.company_id.std_price_neg_threshold
        return threshold

    @api.multi
    def _evaluate_threshold(self, bottom_th, computed_th, diff):
        """ Checks if bottom threshold is reached by computed threshold """
        precision_id = self.env['decimal.precision'].precision_get('Account')
        return float_is_zero(diff, precision_id) or (
            self.standard_price and diff < 0 and computed_th > bottom_th)

    @api.multi
    def compute_segmetation_price(self, cron=None, wizard=None):
        for rec in self:
            rec.product_variant_ids.compute_segmetation_price(cron, wizard)
        return True


class StockChangeStandardPrice(models.TransientModel):
    _inherit = "stock.change.standard.price"

    @api.multi
    def change_price(self):
        res = super(StockChangeStandardPrice, self).change_price()

        if self.env.context.get('from_wizard', False):
            products = self.env[self._context['active_model']].browse(
                self._context['active_id'])
            products.compute_segmetation_price(wizard=True)

        return res
