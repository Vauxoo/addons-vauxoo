from odoo import _, models
from odoo.exceptions import AccessError


class IrRule(models.Model):
    _inherit = "ir.rule"

    def _make_access_error(self, operation, records):
        """Ensure that the selected journal is accessible for the user's team/branch.
        If no team are defined for the journal, access is open to all users.
        """
        if records and records._name == "account.move":
            journals = records.mapped("journal_id").sudo()
            if journals:
                journal_names = ", ".join(journals.mapped("display_name"))
                records.invalidate_recordset()
                return AccessError(
                    _(
                        "You do not have access to the selected journal(s) for this operation.\n"
                        "Journal(s): %s \n\n"
                        "Please select a journal that corresponds to your branch.",
                        journal_names,
                    )
                )
        return super()._make_access_error(operation, records)
