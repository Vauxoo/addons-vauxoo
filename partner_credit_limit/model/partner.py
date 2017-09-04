# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from datetime import timedelta
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    grace_payment_days = fields.Float(
        'Days grace payment',
        help='Days grace payment')

    credit_overloaded = fields.Boolean(
        compute='_get_credit_overloaded',
        string="Credit Overloaded", type='Boolean',
        help="Indicates when the customer has credit overloaded")
    overdue_credit = fields.Boolean(
        compute='_get_overdue_credit', string="Late Payments", type='Boolean',
        help="Indicates when the customer has late payments")
    allowed_sale = fields.Boolean(
        compute='get_allowed_sale', string="Allowed Sales", type='Boolean',
        help="If the Partner has credit overloaded or late payments,"
        " he can't validate invoices and sale orders.")

    @api.multi
    def _get_credit_overloaded(self):
        company = self.env.user.company_id
        for partner in self:
            new_amount = self.env.context.get('new_amount', 0.0)
            new_currency = self.env.context.get('new_currency', False)
            new_amount_currency = new_amount
            if new_currency and company.currency_id != new_currency:
                new_amount_currency = new_currency.compute(
                    new_amount, company.currency_id)

            new_credit = partner.credit + new_amount_currency
            partner.credit_overloaded = new_credit > partner.credit_limit

    @api.model
    def movelines_domain(self, partner):
        domain = [('partner_id', '=', partner.id),
                  ('account_id.internal_type', '=', 'receivable'),
                  ('move_id.state', '!=', 'draft'),
                  ('reconciled', '=', False)]
        return domain

    @api.model
    def debit_credit_maturity(self, movelines):
        debit_maturity, credit_maturity = 0.0, 0.0
        for line in movelines:
            limit_day = line.date_maturity
            if line.partner_id.grace_payment_days:
                maturity = fields.Datetime.from_string(
                    line.date_maturity)
                grace_payment_days = timedelta(
                    days=line.partner_id.grace_payment_days)
                limit_day = maturity + grace_payment_days
                limit_day = limit_day.strftime("%Y-%m-%d")

            if limit_day <= fields.Date.today():
                # credit and debit maturity sums all aml
                # with late payments
                debit_maturity += line.debit
            credit_maturity += line.credit
        return debit_maturity, credit_maturity

    @api.multi
    def _get_overdue_credit(self):
        moveline_obj = self.env['account.move.line']
        for partner in self:
            domain = self.movelines_domain(partner)
            movelines = moveline_obj.search(domain)
            debit_maturity, credit_maturity = self.debit_credit_maturity(
                movelines)
            balance_maturity = debit_maturity - credit_maturity
            partner.overdue_credit = balance_maturity > 0.0

    @api.multi
    def get_allowed_sale(self):
        for partner in self:
            partner.allowed_sale = not partner.credit_overloaded and \
                not partner.overdue_credit
