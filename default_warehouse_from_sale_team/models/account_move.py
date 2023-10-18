from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _search_default_journal(self):
        """If a team is provided and it has a sales journal set, take it as 1st alternative"""
        journal = super()._search_default_journal()
        team = self.env.context.get("salesteam") or self.team_id or self.env.user.sale_team_id
        journal_on_team = team._get_default_journal([journal.type or "general"])
        return journal_on_team or journal

    @api.onchange("team_id")
    def _onchange_team_id(self):
        if self.state != "draft" or not self.is_invoice(include_receipts=True) or not self.team_id.journal_team_ids:
            return {}
        self = self.with_company(self.company_id)
        default_journal_ctx = {
            "default_move_type": self.move_type,
            "default_currency_id": self.currency_id.id,
        }
        default_journal = self.with_context(**default_journal_ctx)._search_default_journal()
        self.journal_id = default_journal
