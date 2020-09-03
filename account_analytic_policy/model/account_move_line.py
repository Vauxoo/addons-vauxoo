from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAccount(models.Model):
    _inherit = "account.account"

    analytic_policy = fields.Selection(
        [('optional', 'Optional'), ('always', 'Always'), ('never', 'Never')],
        default='optional',
        help='"Optional": , the accountant is free to put an analytic account '
             'on an account move line;\n'
             '"Always": the accountant will get an error message if there is '
             'no analytic account;\n'
             '"Never": the accountant will get an error message if an '
             'analytic account is present.'
    )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.multi
    def _is_analytic_policy_ok(self, vals):
        account = self.env['account.account']
        analytic = self.env['account.analytic.account']
        for record in self:
            account = (account.browse(vals['account_id'])
                       if ('account_id' in vals) else record.account_id)
            analytic = (
                analytic.browse(
                    vals['analytic_account_id']) if (
                        'analytic_account_id' in vals)
                else record.analytic_account_id)
            policy = account.analytic_policy
            if not policy or policy == 'optional':
                continue
            if policy == 'never' and analytic:
                raise UserError(_(
                    'You cannot use analytic accounts on a move line with '
                    'Analytic Policy "Never" contact the account manager or '
                    'fix the account configuration or pick another '
                    'account.\n\n') + '%s' % account.name_get())
            if policy == 'always' and not analytic:
                raise UserError(_(
                    'You must use analytic accounts on a move line with '
                    'Analytic Policy "Always" contact the account manager '
                    'or fix the account configuration or pick another '
                    'account.\n\n') + '%s' % account.name_get())
        return True

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._is_analytic_policy_ok(vals)
        return res

    @api.multi
    def write(self, vals):
        self._is_analytic_policy_ok(vals)
        return super().write(vals)
