# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models, api, _
from odoo.exceptions import ValidationError


class AccontInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def check_payment_type(self):
        if self.filtered(lambda invoice:
                         invoice.payment_term_id.payment_type != 'credit'):
            return True

    @api.multi
    def check_limit_credit(self):
        if self.filtered(lambda inv: inv.check_payment_type() or
                         inv.type != 'out_invoice'):
            return True
        for invoice in self:
            msg = invoice.partner_id.with_context(
                new_amount=invoice.amount_total,
                new_currency=invoice.currency_id)._check_credit_limit(model_name=_('Invoice'))
            if not msg:
                continue
            raise ValidationError(msg)
        return True

    @api.multi
    def action_invoice_open(self):
        self.check_limit_credit()
        res = super(AccontInvoice, self).action_invoice_open()
        return res
