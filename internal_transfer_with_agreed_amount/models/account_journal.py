import ast

from odoo import models
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def open_internal_transfers_payments_action(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("account.action_account_all_payments")
        action["context"] = dict(
            ast.literal_eval(action.get("context") or "{}"),
            default_journal_id=self.id,
            search_default_journal_id=self.id,
            search_default_internal_transfer=True,
        )
        return action

    def open_action_internal_transfer(self):
        if not self.company_id.transfer_account_id:
            raise UserError(
                self.env._(
                    'Company "%s" does not have an internal transfer account configured. '
                    "Please set it in Accounting > Configuration > Settings.",
                    self.company_id.display_name,
                )
            )
        ctx = self.env.context.copy()
        ctx.update({"default_journal_id": self.id})
        return {
            "name": self.env._("Internal Transfer"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "internal.transfer.multicurrency",
            "target": "new",
            "context": ctx,
        }
