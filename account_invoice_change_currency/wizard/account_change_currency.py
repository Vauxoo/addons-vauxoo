# -*- encoding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class account_change_currency(models.TransientModel):
    _name = 'account.change.currency'
    _description = 'Change Currency'

    currency_id = fields.Many2one(
        'res.currency',
        string='Change to',
        required=True,
        help="Select a currency to apply on the invoice")

    @api.multi
    def get_invoice(self):
        self.ensure_one()
        invoice = self.env['account.invoice'].browse(
            self._context.get('active_id', False))
        if not invoice:
            raise ValidationError(_('No Invoice on context as "active_id"'))
        return invoice

    @api.onchange('currency_id')
    def onchange_currency(self):
        invoice = self.get_invoice()
        if self.currency_id == invoice.currency_id:
            raise ValidationError(_(
                'Old Currency And New Currency can not be the same'))

    @api.multi
    def change_currency(self):
        """We overwrite original function to simplify and add functionality
        descrived on the manifest
        """
        self.ensure_one()
        invoice = self.get_invoice()
        rate = self.currency_id.rate
        message = _("Currency changed from %s to %s with rate %s") % (
            invoice.currency_id.name, self.currency_id.name,
            rate)
        for line in invoice.invoice_line_ids:
            new_price = 0
            if invoice.company_id.currency_id == invoice.currency_id:
                new_price = line.price_unit * rate
                if new_price <= 0:
                    raise ValidationError(_(
                        'New currency is not configured properly.'))
            if (invoice.company_id.currency_id != invoice.currency_id and
                    invoice.company_id.currency_id == self.currency_id):
                old_rate = invoice.currency_id.rate
                if old_rate <= 0:
                    raise ValidationError(_(
                        'Current currency is not configured properly.'))
                new_price = line.price_unit / old_rate

            if (invoice.company_id.currency_id != invoice.currency_id and
                    invoice.company_id.currency_id != self.currency_id):
                old_rate = invoice.currency_id.rate
                if old_rate <= 0:
                    raise ValidationError(_(
                        'Current currency is not configured properly.'))
                new_price = line.price_unit / old_rate
                new_price *= rate
            line.write({'price_unit': new_price})
        invoice.write({'currency_id': self.currency_id.id})
        # update manual taxes
        for line in invoice.tax_line_ids.filtered(lambda x: x.manual):
            line.amount = self.currency_id.round(line.amount * rate)
        invoice.compute_taxes()
        invoice.message_post(message)
        return {'type': 'ir.actions.act_window_close'}
