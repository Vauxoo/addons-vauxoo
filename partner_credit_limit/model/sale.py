# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: hugo@vauxoo.com
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################
from openerp import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_credit_limit = fields.Float(
        related='partner_id.credit_limit',
        string="Partner Credit Limit",
        readonly=True)
    partner_credit_available = fields.Float(
        related="partner_id.credit_available",
        string="Partner Available Credit",
        readonly=True)
    requested_credit = fields.Float(
        related="amount_total",
        string="Requested Credit")
    partner_overdue_payments_ids = fields.One2many(
        related='partner_id.overdue_payments_ids',
        string='Partner Overdue Payments Items',
        readonly=True)
    partner_pending_payments_ids = fields.One2many(
        related='partner_id.pending_payments_ids',
        string='Partner Pending Payments Items',
        readonly=True)
    partner_overdue_amount = fields.Float(
        related='partner_id.overdue_amount',
        string='Partner Overdue Amount',
        readonly=True)
    payment_terms_ids = fields.Many2many(
        related='partner_id.payment_terms_ids',
        string="Allowed Payment Terms")

    @api.multi
    def check_limit(self):
        for so in self:
            if so.payment_term.payment_type != 'credit':
                return True
            partner = self.env['res.partner'].with_context(
                {'new_amount': so.amount_total,
                 'new_currency': so.company_id.currency_id.id}).browse(
                     so.partner_id.id)
            if partner.allowed_sale:
                return True
            else:
                msg = _('<div><p>The Sale order pass to state of '
                        '<b>Exception Credit</b>.\n '
                        '<br>The partner <b>%s</b>:') % (partner.name)
                if partner.credit_overloaded:
                    msg += _('\n<br><br>Have exceeded the credit limit.'
                             '\n<br>The credit available is $%s'
                             '\n<br>And the credit is being'
                             ' requested is $%s') % \
                        (str((partner.credit_limit - partner.credit)),
                         str(so.amount_total))
                if partner.overdue_credit:
                    max_date = max(self.partner_overdue_payments_ids.mapped(
                        'date_maturity'))
                    msg += _('\n<br><br>It has the overdue payment period.'
                             '\n<br>The expiration date was %s, '
                             '<br>the amount payable is: $%s') % \
                        (max_date, str(self.partner_overdue_amount))
                message = msg
                self.message_post(subject=_("Exception Credit"), body=message)
