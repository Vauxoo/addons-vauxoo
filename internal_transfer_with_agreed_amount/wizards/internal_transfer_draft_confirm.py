from odoo import api, fields, models
from odoo.exceptions import UserError


class InternalTransferDraftConfirm(models.TransientModel):
    _name = "internal.transfer.draft.confirm"
    _description = "Confirm Reset to Draft of Internal Transfer Payments"

    payment_id = fields.Many2one("account.payment", required=True)
    paired_payment_id = fields.Many2one("account.payment", required=True)
    message = fields.Html(compute="_compute_message")

    @api.depends("paired_payment_id")
    def _compute_message(self):
        for rec in self:
            rec.message = self.env._(
                "This payment is part of an internal transfer. Resetting it to draft "
                "will also reset the related payment %s and remove the reconciliation "
                "between both payments. Do you want to continue?",
                rec.paired_payment_id._get_html_link(),
            )

    def action_confirm(self):
        self.ensure_one()
        payments = self.payment_id | self.paired_payment_id

        matched = payments.filtered("is_matched")
        if matched:
            raise UserError(
                self.env._(
                    "The following payments are already matched to a bank statement line "
                    "and cannot be reset to draft: %s",
                    ", ".join(matched.mapped("display_name")),
                )
            )

        transfer_account = self.payment_id.company_id.transfer_account_id
        transfer_lines = payments.move_id.line_ids.filtered(lambda line: line.account_id == transfer_account)
        transfer_lines.remove_move_reconcile()

        payments.with_context(skip_internal_transfer_pair_handling=True).action_draft()

        return {"type": "ir.actions.act_window_close"}
