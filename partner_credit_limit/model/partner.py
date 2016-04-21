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
from openerp import models, fields, api
from datetime import timedelta


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
        for partner in self:
            context = self.env.context or {}
            currency_obj = self.env['res.currency']
            res_company = self.env['res.company']
            imd_obj = self.env['ir.model.data']
            company_id = imd_obj.get_object_reference(
                'base', 'main_company')[1]
            company = res_company.browse(company_id)
            new_amount = context.get('new_amount', 0.0)
            new_currency = context.get('new_currency', False)
            if new_currency:
                from_currency = currency_obj.browse(new_currency)
            else:
                from_currency = company.currency_id
            new_amount_currency = from_currency.compute(
                new_amount, company.currency_id)

            new_credit = partner.credit + new_amount_currency
            partner.credit_overloaded = new_credit > partner.credit_limit

    @api.multi
    def _get_overdue_credit(self):
        for partner in self:
            moveline_obj = self.env['account.move.line']
            movelines = moveline_obj.search(
                [('partner_id', '=', partner.id),
                 ('account_id.type', '=', 'receivable'),
                 ('state', '!=', 'draft'), ('reconcile_id', '=', False)])
            # credit = 0.0
            debit_maturity, credit_maturity = 0.0, 0.0
            for line in movelines:
                if line.date_maturity and line.partner_id.grace_payment_days:
                    maturity = fields.Datetime.from_string(
                        line.date_maturity)
                    grace_payment_days = timedelta(
                        days=line.partner_id.grace_payment_days)
                    limit_day = maturity + grace_payment_days
                    limit_day = limit_day.strftime("%Y-%m-%d")

                elif line.date_maturity:
                    limit_day = line.date_maturity
                else:
                    limit_day = fields.Date.today()
                if limit_day <= fields.Date.today():
                    # credit and debit maturity sums all aml
                    # with late payments
                    debit_maturity += line.debit
                credit_maturity += line.credit
                # credit += line.credit
            balance_maturity = debit_maturity - credit_maturity
            partner.overdue_credit = balance_maturity > 0.0

    @api.multi
    def get_allowed_sale(self):
        for partner in self:
            partner.allowed_sale = not partner.credit_overloaded and \
                not partner.overdue_credit
