# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def check_payment_type(self):
        if self.filtered(lambda so:
                         so.payment_term_id.payment_type != 'credit'):
            return True

    @api.multi
    def check_limit(self):
        if self.filtered(lambda so: so.check_payment_type()):
            return True
        for so in self:
            msg = so.partner_id.with_context(
                new_amount=so.amount_total,
                new_currency=so.currency_id)._check_credit_limit(model_name=_('Sale Order'))
            if not msg:
                continue
            raise ValidationError(msg)
        return True

    @api.multi
    def action_confirm(self):
        self.check_limit()
        return super(SaleOrder, self).action_confirm()
