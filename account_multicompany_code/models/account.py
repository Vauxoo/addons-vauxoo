from odoo import api, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.multi
    def name_get(self):
        result = dict(super(AccountAccount, self).name_get())
        for record in self:
            if record.company_id.code:
                result[record.id] += ' (%s)' % record.company_id.code
        return list(result.items())


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.multi
    def name_get(self):
        result = dict(super(AccountJournal, self).name_get())
        for record in self:
            if record.company_id.code:
                result[record.id] += ' (%s)' % record.company_id.code
        return list(result.items())
