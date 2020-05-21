from odoo import models, api, _
from odoo import exceptions


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def check_payment_type(self):
        if self.filtered(lambda so:
                         so.payment_term_id.payment_type != 'credit'):
            return True

    def check_limit(self):
        if self.filtered(lambda so: so.check_payment_type()):
            return True
        for so in self:
            allowed_sale = so.partner_id.with_context(
                {'new_amount': so.amount_total,
                 'new_currency': so.currency_id}).allowed_sale
            if allowed_sale:
                return True
            else:
                msg = _('Can not confirm the Sale Order because Partner '
                        'has late payments or has exceeded the credit limit.'
                        '\nPlease cover the late payment or check credit limit'
                        '\nCredit Limit : %s') % (so.partner_id.credit_limit)
                raise exceptions.Warning(msg)

    def action_confirm(self):
        self.check_limit()
        return super(SaleOrder, self).action_confirm()
