from odoo import api, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    @api.depends("company_id.code")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        for account in self.filtered("company_id.code"):
            account.display_name += " (%s)" % account.company_id.code
        return res
