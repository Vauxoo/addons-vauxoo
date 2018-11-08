# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models, api, _
from odoo import exceptions


class AccontInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def check_payment_type(self):
        if self.filtered(lambda invoice:
                         invoice.payment_term_id.payment_type != 'credit'):
            return True

    @api.multi
    def check_limit_credit(self):
        if self.filtered(lambda inv: inv.check_payment_type() or
                         inv.type != 'out_invoice'):
            return True
        for invoice in self:
            allowed_sale = invoice.partner_id.with_context(
                {'new_amount': invoice.amount_total,
                 'new_currency': invoice.currency_id}).allowed_sale
            if allowed_sale:
                return True
            else:
                msg = _('Can not validate the Invoice because Partner '
                        'has late payments or has exceeded the credit limit.'
                        '\nPlease cover the late payment or check credit limit'
                        '\nCredit'
                        ' Limit : %s') % (invoice.partner_id.credit_limit)
                raise exceptions.Warning(msg)

    @api.multi
    def action_invoice_open(self):
        self.check_limit_credit()
        res = super(AccontInvoice, self).action_invoice_open()
        return res
