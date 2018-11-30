from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('date_invoice', 'index_based_currency_id',
                 'company_currency_id', 'currency_id')
    def _compute_currency_rate(self):
        for inv in self:
            inv.index_based_currency_rate = 1
            inv.currency_rate = (
                inv.currency_id._convert(
                    1, inv.index_based_currency_id, inv.company_id,
                    inv.date_invoice or fields.Date.today(), round=False))
            inv.company_currency_rate = (
                inv.company_currency_id._convert(
                    1, inv.index_based_currency_id, inv.company_id,
                    inv.date_invoice or fields.Date.today(), round=False))

    @api.depends('amount_total_signed', 'agreement_currency_rate',
                 'date_invoice')
    def _compute_currency_amount(self):
        for inv in self:
            index_based_currency_amount = inv.amount_total_signed
            if inv.index_based_currency_id != inv.currency_id:
                index_based_currency_amount = inv.currency_id._convert(
                    inv.amount_total_signed, inv.index_based_currency_id,
                    inv.company_id, inv.date_invoice or fields.Date.today())
            inv.index_based_currency_amount = index_based_currency_amount
            inv.agreement_currency_amount = (
                inv.index_based_currency_amount / inv.agreement_currency_rate)

    @api.onchange('agreement_currency_rate')
    def onchange_agreement_currency_rate(self):
        if self.agreement_currency_rate <= 0:
            raise UserError(_('Invalid currency rate value'))

    @api.onchange('agreement_currency_id')
    def onchange_agreement_currency_id(self):
        self.agreement_currency_rate = self.agreement_currency_id._convert(
            1, self.index_based_currency_id,
            self.company_id,
            self.date_invoice or fields.Date.today(), round=False)
        self.agreement_currency_amount = self.index_based_currency_id._convert(
            self.index_based_currency_amount, self.agreement_currency_id,
            self.company_id,
            self.date_invoice or fields.Date.today(), round=False)

    @api.model
    def default_get(self, default_fields):
        res = super(AccountInvoice, self).default_get(default_fields)
        default_rate = (
            self.env.user.company_id.currency_id._convert(
                1, self.env.user.company_id.index_based_currency_id,
                self.env.user.company_id,
                self.date_invoice or fields.Date.today(), round=False))
        res['agreement_currency_id'] = self.env.user.company_id.currency_id.id
        res['agreement_currency_rate'] = default_rate
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
    agreement_currency_amount = fields.Monetary(
        currency_field='agreement_currency_id',
        store=True, compute='_compute_currency_amount',
        copy=False,
        help="Total amount in the currency of the company, negative for "
        "credit notes.")
    index_based_currency_rate = fields.Float(
        default=1,
        store=True, compute='_compute_currency_rate',
        help='Technical field for Index based currency rate',
        copy=False, digits=(12, 6))
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
        readonly=True, states={'draft': [('readonly', False)]},
        copy=True, digits=(12, 6))

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        res = super(AccountInvoice, self).finalize_invoice_move_lines(
            move_lines)
        for line in res:
            line[2]['currency_rate'] = self.currency_rate
            line[2]['agreement_currency_rate'] = self.agreement_currency_rate
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    currency_rate = fields.Float(
        help="Document currency rate at date of document creation or "
        "document approval against Index Based Currency",
        copy=False, digits=(12, 6))
    agreement_currency_rate = fields.Float(
        help="Currency rate this Document was agreed",
        copy=True, digits=(12, 6))
    index_based_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.index_based_currency_id',
        help="Currency used por reporting purposes",
        store=True)
