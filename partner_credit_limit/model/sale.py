# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openerp import models, api, _
from openerp import exceptions


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def check_limit(self):
        for so in self:
            if so.payment_term.payment_type != 'credit':
                return True
            allowed_sale = self.env['res.partner'].with_context(
                {'new_amount': so.amount_total,
                 'new_currency': so.company_id.currency_id.id}).browse(
                     so.partner_id.id).allowed_sale
            if allowed_sale:
                return True
            else:
                msg = _('Can not confirm the Sale Order because Partner '
                        'has late payments or has exceeded the credit limit.'
                        '\nPlease cover the late payment or check credit limit'
                        '\nCreadit Limit : %s') % (so.partner_id.credit_limit)
                raise exceptions.Warning(('Warning!'), msg)
