from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    section_id = fields.Many2one("crm.team", string="Sales Team")
    # Avoid access errors when user has access to a journal item but
    # not to its journal, e.g. when reconciling bank statements.
    display_name = fields.Char(compute="_compute_display_name", compute_sudo=True)
