from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('team_id')
    def sale_team_change(self):
        if (self.state != 'draft' or not self.team_id or
                not self.team_id.journal_team_ids):
            return
        default_journals = self.team_id.journal_team_ids.filtered(
            lambda x: x.type == 'sale')
        if default_journals:
            self.journal_id = default_journals[0]
