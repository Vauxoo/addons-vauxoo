# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, api, fields, _


class AccountPaymentTerm(models.Model):

    _inherit = 'account.payment.term'

    @api.multi
    @api.depends('line_ids')
    def _compute_payment_type(self):
        """This method compute the Payment type
            It is cash when payment term
            has only one line to compute,
            It is credit when payment term has
            at least two line to compute
        """
        key_payment = "account.payment_term_type"
        payment_type = self.env[
            "ir.config_parameter"].sudo().get_param(
                key_payment, default='bqp')
        p_type = {
            'bqp': lambda a: 'credit' if a.line_ids else 'cash',
            'bdp': lambda a: 'credit' if a.line_ids.filtered(
                lambda e: e.days > 0) else 'cash'}
        for record in self:
            record.payment_type = p_type.get(
                payment_type, lambda a: 'cash')(record)

    payment_type = fields.Selection(
        [('credit', _('Credit')),
         ('cash', _('Cash'))],
        string="Payment Type", compute='_compute_payment_type')
