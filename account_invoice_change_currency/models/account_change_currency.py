# -*- encoding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    old_currency_id = fields.Many2one('res.currency')
    custom_rate = fields.Float(compute='_compute_custome_rate_currency',
                               inverse='_inverse_custom_rate_currency',
                               required=True, help="Set new currency rate to "
                               "apply on the invoice\n.This rate will be taken"
                               " in order to convert amounts between the "
                               "currency on the invoice and MX currency",
                               digits=(12, 6), store=True)

    @api.model
    def create(self, values):
        values['old_currency_id'] = values['currency_id']
        return  super(AccountInvoice, self).create(values)

    @api.multi
    def _inverse_custom_rate_currency(self):
        for inv in self:
            pass

    @api.depends('currency_id')
    @api.multi
    def _compute_custome_rate_currency(self):
        for inv in self:
            # custom_rate = 1.0
            # if inv.currency_id.name != 'MXN':
            #     ctx = dict(company_id=inv.company_id.id, date=inv.date_invoice)
            #     mxn = self.env.ref('base.MXN').with_context(ctx)
            #     invoice_currency = inv.currency_id.with_context(ctx)
            #     custom_rate = invoice_currency.compute(1, mxn, False)
            # inv.custom_rate = custom_rate
            ctx = dict(company_id=inv.company_id.id, date=inv.date_invoice)
            inv.custom_rate = inv.with_context(ctx).currency_id.rate # _custom_rate

    @api.multi
    def action_account_change_currency(self):
        for inv in self:
            ctx = dict(company_id=inv.company_id.id, date=inv.date_invoice)
            rate = inv.custom_rate
            old_currency = inv.with_context(ctx).old_currency_id
            c_currency = inv.company_id.with_context(ctx).currency_id
            new_currency = inv.with_context(ctx).currency_id
            message = _("Currency changed from %s to %s with rate %s") % (
                old_currency.name, new_currency.name, rate)
            for line in inv.invoice_line_ids:
                new_price = 0
                if c_currency == new_currency:
                    new_price = line.price_unit * rate
                    if new_price <= 0:
                        raise ValidationError(_(
                            'New currency is not configured properly.'))
                if c_currency != old_currency and c_currency == new_currency:
                    old_rate = old_currency.rate
                    if old_rate <= 0:
                        raise ValidationError(_(
                            'Current currency is not configured properly.'))
                    new_price = line.price_unit / old_rate

                if c_currency != old_currency and c_currency != new_currency:
                    old_rate = old_currency.rate
                    if old_rate <= 0:
                        raise ValidationError(_(
                            'Current currency is not configured properly.'))
                    new_price = line.price_unit / old_rate
                    new_price *= rate
                if c_currency == old_currency and c_currency != new_currency:
                    new_price = line.price_unit * rate
                    if new_price <= 0:
                        raise ValidationError(_(
                            'New currency is not configured properly.'))
                line.write({'price_unit': new_price})
            inv.write({'old_currency_id': new_currency.id})
            # update manual taxes
            for line in inv.tax_line_ids.filtered(lambda x: x.manual):
                line.amount = new_currency.round(line.amount * rate)
            inv.compute_taxes()
            inv.message_post(message)
            return {'type': 'ir.actions.act_window_close'}
