from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    section_id = fields.Many2one('crm.team', string='Sales Team')

    def name_get(self):
        """Avoid access errors when computing journal's display name

        Avoid access errors when user has access to a journal item but not to its journal, e.g. when
        reconciling bank statements.
        """
        self = self.sudo()
        return super().name_get()
