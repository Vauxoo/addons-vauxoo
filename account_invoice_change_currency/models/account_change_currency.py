from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    old_currency_id = fields.Many2one('res.currency')
    custom_rate = fields.Float(
        compute='_compute_custome_rate_currency',
        inverse='_inverse_custom_rate_currency',
        required=True, help="Set new currency rate to apply on the invoice\n."
        "This rate will be taken in order to convert amounts between the "
        "currency on the invoice and MX currency",
        store=True)

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
            custom_rate = 1.0
            if inv.currency_id.name != 'MXN':
                ctx = dict(company_id=inv.company_id.id, date=inv.date_invoice)
                mxn = self.env.ref('base.MXN').with_context(ctx)
                invoice_currency = inv.currency_id.with_context(ctx)
                custom_rate = invoice_currency.compute(1, mxn, False)
            inv.custom_rate = custom_rate

    @api.multi
    def action_account_change_currency(self):
        """ This Allows you  Change currency between company currency and
        Invoice currency.
        Firts Case:
            Convert from original currency to MXN(company currency). taking the
            custom rate. e.g.:
                1.- Original USD and New currency are USD
                2.- Covert USD to MXN with custom rate
        Second Case:
            The original Currency was changed to different currency than MXN
            then convert from original currency to MXN, taking default rate
            because custom rate is between new currency and MXN after that
            now convert MXN to new currency taking custom rate. e.g.:
                Original currency USD
                New currency EUR (this has the custom rate EUR vs MXN)
                1.- USD to MXN with default rate
                2.- MXN to EUR with custom rate
        Third Case:
            Original Currency is MXN(company currency) and new currency is any
            different than MXN, e.g.:
                MXN To USD
        """
        for inv in self:
            ctx = dict(company_id=inv.company_id.id, date=inv.date_invoice)
            inv = inv.with_context(ctx)
            old_currency = inv.old_currency_id
            c_currency = inv.company_id.currency_id
            new_currency = inv.currency_id
            custom_rate = 1 / inv.custom_rate
            messages_error = _('Current currency is not configured properly.')
            for line in inv.invoice_line_ids:
                new_price = 0
                final_currency = False
                if c_currency == old_currency and c_currency == new_currency:
                    final_currency = c_currency
                    continue
                # First Case
                if old_currency == new_currency and old_currency != c_currency:
                    new_price = line.price_unit / custom_rate
                    final_currency = c_currency
                    if new_price <= 0:
                        raise ValidationError(messages_error)
                if (old_currency != c_currency and old_currency != new_currency
                        and new_currency == c_currency):
                    raise ValidationError(
                        _("The conversion to %s is automatic.\nIt's not needed"
                          " change currency vaulue, just press the 'Change' "
                          "button.")% new_currency.name)
                # Second Case
                if (old_currency != c_currency and old_currency != new_currency
                        and c_currency not in (old_currency, new_currency)):
                    old_rate = old_currency.rate
                    if old_rate <= 0:
                        raise ValidationError(messages_error)
                    new_price = line.price_unit / old_rate
                    new_price *= custom_rate
                    final_currency = new_currency
                # Third Case
                if old_currency == c_currency and new_currency != c_currency:
                    final_currency = new_currency
                    new_price = line.price_unit * custom_rate
                    if new_price <= 0:
                        raise ValidationError(messages_error)
                line.write({'price_unit': new_price})
            inv.write({'old_currency_id': final_currency.id,
                       'currency_id': final_currency.id})
            # update manual taxes
            for line in inv.tax_line_ids.filtered(lambda x: x.manual):
                line.amount = new_currency.round(line.amount * custom_rate)
            inv.compute_taxes()
            message = _("Currency changed from %s to %s with rate %s") % (
                old_currency.name, new_currency.name, custom_rate)
            inv.message_post(message)
