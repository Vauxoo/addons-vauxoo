# -*- coding: utf-8 -*-
# Copyright 2017 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('partner_id')
    def onchange_partner_id_dtype(self):
        carrier_obj = self.env['delivery.carrier']
        # do nothing without partner
        if not self.partner_id:
            return
        # get carriers available based on partner address information
        carrier_ids = [
            carrier.id for carrier in carrier_obj.search([])
            if carrier.verify_carrier(
                self.partner_shipping_id or self.partner_id)]
        # filter carriers by order amount
        for carrier in carrier_obj.browse(carrier_ids):
            try:
                carrier.get_price_available(self)
            except UserError as e:
                _logger.info(
                    "Carrier %s is no a suitable delivery method for %s..."
                    " Exception: %s", self.name, self.partner_id.name, e.name)
                carrier_ids.remove(carrier.id)
        # return all carriers available after apply address and amount filters
        return {'domain': {
            'carrier_id': carrier_ids and [('id', 'in', carrier_ids)],
        }}
