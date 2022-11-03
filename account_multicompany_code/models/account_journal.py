from odoo import models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def name_get(self):
        result = dict(super().name_get())
        for record in self:
            if record.company_id.code:
                result[record.id] += " (%s)" % record.company_id.code
        return list(result.items())
