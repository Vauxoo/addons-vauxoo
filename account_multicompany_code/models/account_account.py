from odoo import api, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    @api.depends("company_ids.code")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        for account in self.filtered(lambda a: a.company_ids):
            codes = ", ".join(account.company_ids.mapped("code"))
            current_display_name = account.display_name or ""
            account.display_name = "%s (%s)" % (current_display_name, codes)
        return res
