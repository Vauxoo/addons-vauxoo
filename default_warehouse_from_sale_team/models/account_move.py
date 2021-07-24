from odoo import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _search_default_journal(self, journal_types):
        """If a team is provided and it has a sales journal set, take it as 1st alternative"""
        team = self.env.context.get("salesteam")
        journal_on_team = None
        if team and journal_types == ["sale"]:
            journal_on_team = team._get_default_journal_sale()
        return journal_on_team or super()._search_default_journal(journal_types)

    @api.onchange('team_id')
    def _onchange_team_id(self):
        if (
            self.state != "draft"
            or not self.team_id
            or self.move_type not in self.get_sale_types(include_receipts=True)
        ):
            return {}
        default_journal = self.team_id._get_default_journal_sale()
        if default_journal:
            self.journal_id = default_journal
