# Copyright 2020 Vauxoo
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"

    section_id = fields.Many2one("crm.team", string="Sale team")

    @api.multi
    def write(self, vals):
        """The workers cache is cleared when the `section_id` field is modified to reflect the changes when the
        following domain is called:
        * `rule_default_warehouse_journal`
        """
        if vals.get("section_id"):
            self.clear_caches()
        return super(AccountJournal, self).write(vals)

    @api.multi
    def create(self, values):
        """The workers cache is cleared to reflect the changes when the following domain is called:
        * `rule_default_warehouse_journal`
        """
        if values.get("section_id"):
            self.clear_caches()
        return super(AccountJournal, self).create(values)

    @api.multi
    def unlink(self):
        """The workers cache is cleared when a record it's deleted,
        """
        self.clear_caches()
        return super(AccountJournal, self).unlink()
