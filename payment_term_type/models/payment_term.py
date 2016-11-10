# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import models, api, fields, _


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
        payment_type = self.env["ir.config_parameter"].get_param(
            key_payment, default='bqp')
        for record in self:
            if payment_type == 'bqp':
                record.payment_type = 'cash'
                if len(record.line_ids) > 1:
                    record.payment_type = 'credit'
            elif payment_type == 'bdp':
                for line in record.line_ids:
                    record.payment_type = 'cash'
                    if line.days > 0:
                        record.payment_type = 'credit'

    payment_type = fields.Selection(
        [('credit', _('Credit')),
         ('cash', _('Cash'))],
        string="Payment Type", compute='_compute_payment_type')
