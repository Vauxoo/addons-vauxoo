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

    def _get_default_journal_sale(self):
        for journal in self.journal_team_ids:
            if journal.type == "sale":
                return journal
        return self.env["account.journal"]
