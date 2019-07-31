# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import time
from datetime import datetime
import dateutil.relativedelta
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

    @tools.ormcache('bom', 'internal')
    def _calc_material_price_seg(self, bom, internal=None, wizard=None):
        price, sgmnt_dict = super(Product, self)._calc_material_price_seg(
            bom, internal, wizard)
        if not bom.sub_products:
            return price, sgmnt_dict

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

        bom_obj = self.env['mrp.bom']

        for sub_prod in bom.sub_products:
            product_id = sub_prod.product_id
            prod_costs_dict = _get_sgmnt(product_id)
            child_bom_id = bom_obj._bom_find(product=product_id)
            if child_bom_id and product_id.cost_method == 'standard':
                prod_costs_dict = self._calc_price_seg(
                    child_bom_id, True, wizard)

            for fieldname in SEGMENTATION_COST:
                # NOTE: Is this price well Normalized
                if not prod_costs_dict[fieldname]:
                    continue
                price_sgmnt = product_id.uom_id._compute_price(
                    prod_costs_dict[fieldname],
                    sub_prod.product_uom_id) * sub_prod.product_qty
                price -= price_sgmnt
                sgmnt_dict[fieldname] -= price_sgmnt
        return price, sgmnt_dict
