# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openerp import models, api, _
from openerp import exceptions


class AccontInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def check_limit_credit(self):
        for invoice in self:
            if invoice.payment_term_id.payment_type != 'credit':
                return True
            allowed_sale = self.env['res.partner'].with_context(
                {'new_amount': invoice.amount_total,
                 'new_currency': invoice.currency_id.id}).browse(
                     invoice.partner_id.id).allowed_sale
            if allowed_sale:
                return True
            else:
                msg = _('Can not validate the Invoice because Partner '
                        'has late payments or has exceeded the credit limit.'
                        '\nPlease cover the late payment or check credit limit'
                        '\nCreadit'
                        ' Limit : %s') % (invoice.partner_id.credit_limit)
                raise exceptions.Warning(_('Warning!'), msg)
