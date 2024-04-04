from odoo import api, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.depends("company_id.code")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        for journal in self.filtered("company_id.code"):
            journal.display_name += " (%s)" % journal.company_id.code
        return res
