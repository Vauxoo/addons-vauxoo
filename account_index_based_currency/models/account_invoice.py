from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.addons.account.models.account_payment import (
    MAP_INVOICE_TYPE_PAYMENT_SIGN)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('date_invoice', 'index_based_currency_id',
                 'company_currency_id', 'currency_id')
    def _compute_currency_rate(self):
        cur_obj = self.env['res.currency']
        for inv in self:
            inv.currency_rate = cur_obj._get_conversion_rate(
                inv.currency_id, inv.index_based_currency_id, inv.company_id,
                inv.date_invoice or fields.Date.today())
            inv.company_currency_rate = cur_obj._get_conversion_rate(
                inv.company_currency_id, inv.index_based_currency_id,
                inv.company_id, inv.date_invoice or fields.Date.today())

    @api.depends('amount_total_signed', 'agreement_currency_rate',
                 'agreement_currency_amount', 'date_invoice')
    def _compute_currency_amount(self):
        for inv in self:
            index_based_currency_amount = inv.amount_total_signed
            if inv.index_based_currency_id != inv.currency_id:
                index_based_currency_amount = inv.currency_id._convert(
                    inv.amount_total_signed, inv.index_based_currency_id,
                    inv.company_id, inv.date_invoice or fields.Date.today())
            inv.index_based_currency_amount = index_based_currency_amount
            inv.transaction_currency_amount = (
                inv.agreement_currency_rate * inv.agreement_currency_amount)

    @api.onchange('agreement_currency_rate')
    def onchange_agreement_currency_rate(self):
        if self.agreement_currency_rate <= 0:
            raise UserError(_('Invalid currency rate value'))

    @api.model
    def default_get(self, default_fields):
        res = super(AccountInvoice, self).default_get(default_fields)
        if 'currency_id' not in res:
            return res
        currency_id = self.currency_id.browse(res.get('currency_id'))
        company_id = self.company_id.browse(res.get('company_id'))
        res['agreement_currency_id'] = currency_id.id
        res['agreement_currency_rate'] = currency_id._get_conversion_rate(
            currency_id, company_id.index_based_currency_id, company_id,
            fields.Date.today())
        return res

    agreement_currency_id = fields.Many2one(
        'res.currency',
        copy=True,
        help="Currency at which the agreement is to be/was settled",
        readonly=True, states={'draft': [('readonly', False)]},
    )
    index_based_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.index_based_currency_id',
        help="Currency used for reporting purposes",
        copy=False)
    index_based_currency_amount = fields.Monetary(
        currency_field='index_based_currency_id',
        store=True, compute='_compute_currency_amount',
        copy=False,
        help="Total amount in the currency of the company, negative for "
        "credit notes.")
    transaction_currency_amount = fields.Monetary(
        currency_field='currency_id',
        copy=False,
        store=True, compute='_compute_currency_amount',
        help="Total amount in the currency of the transaction in accordance "
        "with the agreement amount and rate.")
    agreement_currency_amount = fields.Monetary(
        currency_field='agreement_currency_id',
        copy=False,
        help="Total amount in the currency of the company, negative for "
        "credit notes.")
    currency_rate = fields.Float(
        help="Document currency rate at date of document creation or "
        "document approval against Index Based Currency",
        store=True, compute='_compute_currency_rate',
        copy=False, digits=(12, 6))
    company_currency_rate = fields.Float(
        help="Company currency rate at date of document creation or "
        "document approval against Index Based Currency",
        store=True, compute='_compute_currency_rate',
        copy=False, digits=(12, 6))
    agreement_currency_rate = fields.Float(
        help="Currency rate this Document was agreed",
        default=1,
        readonly=True, states={'draft': [('readonly', False)]},
        copy=True, digits=(12, 6))

    def finalize_invoice_move_lines(self, move_lines):
        res = super(AccountInvoice, self).finalize_invoice_move_lines(
            move_lines)
        if self.currency_id == self.agreement_currency_id:
            return res
        for line in (line for line in res
                     if line[2]['account_id'] == self.account_id.id):
            line[2]['agreement_currency_id'] = self.agreement_currency_id.id
            line[2]['agreement_currency_amount'] = (
                MAP_INVOICE_TYPE_PAYMENT_SIGN[self.type] *
                self.agreement_currency_amount)
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    index_based_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.index_based_currency_id',
        help="Currency used por reporting purposes",
        store=True)
    agreement_currency_id = fields.Many2one(
        'res.currency',
        copy=False,
        help="Currency at which the agreement is to be/was settled",
    )
    agreement_currency_amount = fields.Monetary(
        currency_field='agreement_currency_id',
        copy=False,
        help="Total amount in the currency of the company, negative for "
        "credit notes.")
