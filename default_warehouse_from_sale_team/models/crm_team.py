from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    default_warehouse_id = fields.Many2one(
        'stock.warehouse',
        help='In this field can be defined a default warehouse for '
        'the related users to the sales team.',
    )
    journal_team_ids = fields.One2many(
        'account.journal', 'section_id', string="Journal's sales teams",
        help="Specify what journals a member of this sales team can see.",
    )
    journal_stock_id = fields.Many2one(
        'account.journal', 'Journal stock valuation',
        help='It indicates the journal to be used when a move line is created with '
        'the warehouse of this sales team',
    )

    def _get_default_team_id(self, user_id=None, domain=None):
        """When specified by context, ensure the sales team is taken from the current user"""
        if (
            user_id is not None
            and self.env.context.get("keep_current_user_salesteam")
            and self.env.user.sale_team_id
        ):
            user_id = self.env.uid
        return super()._get_default_team_id(user_id=user_id, domain=domain)

    def _get_default_journal(self, journal_types):
        journal = self.env["account.journal"]
        if not self or set(journal_types) == {"general"}:
            return journal
        company = self.env["res.company"].browse(self.env.context.get("default_company_id")) or self.env.company
        company_currency = company.currency_id
        currency_ids = [self.env.context.get("default_currency_id") or company_currency.id]
        if currency_ids == company_currency.ids:
            currency_ids.append(False)
        domain = [
            ("section_id", "=", self.id),
            ("company_id", "=", company.id),
            ("type", "in", journal_types),
        ]
        domain_currency = domain + [("currency_id", "in", currency_ids)]
        return journal.search(domain_currency, limit=1) or journal.search(domain, limit=1)
