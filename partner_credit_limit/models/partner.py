from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

NO_BREAK_SPACE = "\u00a0"
TAB_SPACE = 4 * NO_BREAK_SPACE


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_limit = fields.Float(company_dependent=True)
    grace_payment_days = fields.Float(
        'Days grace payment',
        help='Days grace payment', company_dependent=True)

    credit_overloaded = fields.Boolean(
        compute='_get_credit_overloaded',
        string="Credit Overloaded", type='Boolean',
        help="Indicates when the customer has credit overloaded")
    overdue_credit = fields.Boolean(
        compute='_get_overdue_credit', string="Late Payments", type='Boolean',
        help="Indicates when the customer has late payments")
    allowed_sale = fields.Boolean(
        compute='get_allowed_sale', string="Allowed Sales", type='Boolean',
        help="If the Partner has credit overloaded or late payments,"
        " he can't validate invoices and sale orders.")

    @api.constrains('grace_payment_days')
    def _check_grace_payment_days_value(self):
        for record in self:
            if not 0 <= record.grace_payment_days <= 999999:
                raise ValidationError(
                    _('Invalid value %s for payment grace days: value must be '
                      'between 0 and 999999.') % record.grace_payment_days)

    @api.multi
    def _get_credit_overloaded(self):
        company = self.env.user.company_id
        for partner in self:
            new_amount = self.env.context.get('new_amount', 0.0)
            new_currency = self.env.context.get('new_currency', False)
            new_amount_currency = new_amount
            if new_currency and company.currency_id != new_currency:
                new_amount_currency = new_currency.compute(
                    new_amount, company.currency_id)

            new_credit = partner.credit + new_amount_currency
            partner.credit_overloaded = new_credit > partner.credit_limit

    @api.model
    def movelines_domain(self, partner):
        """Return the domain for search the
        account.move.line for the user's company."""
        domain = [('partner_id', '=', partner.id),
                  ('company_id', '=', self.env.user.company_id.id),
                  ('account_id.internal_type', '=', 'receivable'),
                  ('move_id.state', '!=', 'draft'),
                  ('reconciled', '=', False)]
        return domain

    @api.model
    def debit_credit_maturity(self, movelines):
        debit_maturity, credit_maturity = 0.0, 0.0
        for line in movelines:
            limit_day = line.date_maturity
            if line.partner_id.grace_payment_days:
                maturity = fields.Datetime.to_datetime(
                    line.date_maturity)
                grace_payment_days = timedelta(
                    days=line.partner_id.grace_payment_days)
                limit_day = maturity + grace_payment_days
                limit_day = fields.Date.to_date(limit_day)

            if limit_day <= fields.Date.today():
                # credit and debit maturity sums all aml
                # with late payments
                debit_maturity += line.debit
            credit_maturity += line.credit
        return debit_maturity, credit_maturity

    @api.multi
    def _get_overdue_credit(self):
        moveline_obj = self.env['account.move.line']
        for partner in self:
            domain = self.movelines_domain(partner)
            movelines = moveline_obj.search(domain)
            debit_maturity, credit_maturity = self.debit_credit_maturity(
                movelines)
            balance_maturity = debit_maturity - credit_maturity
            partner.overdue_credit = balance_maturity > 0.0

    @api.multi
    def get_allowed_sale(self):
        for partner in self:
            partner.allowed_sale = not partner.credit_overloaded and \
                not partner.overdue_credit

    def _check_credit_limit(self, model_name=False):
        """Method that will return a message when the partner has late payments and/or has exceeded the credit limit.
        """
        self.ensure_one()
        if self.allowed_sale:
            return False
        credit_overloaded = self.credit_overloaded
        overdue_credit = self.overdue_credit
        msg = _('Can not confirm the %s because the Partner:\n') % (model_name and model_name or _('record'))
        do_msg = _('Please: \n')

        if overdue_credit:
            msg += TAB_SPACE + _('• Has late payments.\n')
            do_msg += TAB_SPACE + _('• Cover the late payments.\n')
        if credit_overloaded:
            msg += TAB_SPACE + _('• Has exceeded the credit limit.\n')
            do_msg += TAB_SPACE + _('• Check credit limit.\n')
            do_msg += TAB_SPACE*2 + _('Credit limit: %s') % self.credit_limit
        return '%s %s' % (msg, do_msg)
