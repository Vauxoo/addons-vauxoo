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

    @api.multi
    @api.depends('payment_terms_ids', 'payment_terms_ids.sequence')
    def _default_payment_term(self):
        for partner in self:
            if partner.payment_terms_ids:
                payment_term = self.env['account.payment.term'].search(
                    [("id", 'in', partner.payment_terms_ids.ids)],
                    order='sequence', limit=1).id
            else:
                payment_term = self.env['ir.values'].get_defaults_dict(
                    'res.partner').get('property_payment_term')
            partner.property_payment_term = payment_term

    def get_domain(self):
        ids = self.env.user.company_id.payment_terms_ids.ids
        return [('id', 'in', ids)]

    grace_payment_days = fields.Float(
        related='property_payment_term.grace_payment_days',
        help='Days grace payment', readonly=True)

    credit_overloaded = fields.Boolean(
        compute='_get_credit_overloaded',
        string="Credit Overloaded", type='Boolean',
        help="Indicates when the customer has credit overloaded")
    overdue_credit = fields.Boolean(
        compute='_get_overdue_credit', string="Late Payments",
        help="Indicates when the customer has late payments")
    allowed_sale = fields.Boolean(
        compute='get_allowed_sale', string="Allowed Sales",
        help="If the Partner has credit overloaded or late payments,"
        " he can't validate invoices and sale orders.")
    credit_available = fields.Float(compute="_get_credit_overloaded",
                                    string="Available Credit")
    overdue_amount = fields.Float(
        compute='_get_overdue_credit', string="Overdue amout",
        help="Payment has to be made for having reached "
             "the maturity date of the obligation.")
    payment_terms_ids = fields.Many2many(
        'account.payment.term', string="Allowed Payment Terms",
        domain=get_domain)
    property_payment_term = fields.Many2one(
        comodel_name="account.payment.term",
        compute=_default_payment_term,
        company_dependent=False,
        store=True)

    overdue_payments_ids = fields.One2many(
        comodel_name="account.move.line",
        inverse_name='partner_id',
        compute="_get_overdue_credit")

    pending_payments_ids = fields.One2many(
        comodel_name="account.move.line",
        inverse_name='partner_id',
        compute="_get_overdue_credit")

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
            credit = partner.credit if partner.credit > 0 else 0
            partner.credit_available = partner.credit_limit - credit

            if new_credit > partner.credit_limit:
                partner.credit_overloaded = True
            else:
                partner.credit_overloaded = False

    @api.multi
    def _get_overdue_credit(self):
        moveline_obj = self.env['account.move.line']
        for partner in self:
            movelines = moveline_obj.search(
                [('partner_id', '=', partner.commercial_partner_id.id),
                 ('account_id.type', '=', 'receivable'),
                 ('debit', '!=', 0),
                 ('state', '!=', 'draft'), ('reconcile_id', '=', False)])
            # credit = 0.0
            debit_maturity, credit_maturity = 0.0, 0.0
            lines = []
            for line in movelines:
                limit_day = self.get_limit_date(line)
                if limit_day <= fields.Date.today():
                    lines.append(line.id)
                    # credit and debit maturity sums all aml
                    # with late payments
                    debit_maturity += line.debit
                credit_maturity += line.credit
                # credit += line.credit
            balance_maturity = debit_maturity - credit_maturity
            partner.overdue_amount = balance_maturity or 0
            partner.overdue_payments_ids = lines
            pending_ids = [move.id for move in movelines
                           if move.id not in lines]
            partner.pending_payments_ids = pending_ids

            if balance_maturity > 0.0:
                partner.overdue_credit = True
            else:
                partner.overdue_credit = False

    def get_limit_date(self, line):
        if line.date_maturity and line.partner_id.grace_payment_days:
            maturity = fields.Datetime.from_string(
                line.date_maturity)
            grace_payment_days = timedelta(
                days=line.partner_id.grace_payment_days)
            limit_day = maturity + grace_payment_days
            limit_day = limit_day.strftime("%Y-%m-%d")
            return limit_day

        elif line.date_maturity:
            limit_day = line.date_maturity
            return limit_day
        else:
            limit_day = fields.Date.today()
            return limit_day

    @api.multi
    def get_allowed_sale(self):
        for partner in self:
            if not partner.credit_overloaded and not partner.overdue_credit:
                partner.allowed_sale = True
            else:
                partner.allowed_sale = False
