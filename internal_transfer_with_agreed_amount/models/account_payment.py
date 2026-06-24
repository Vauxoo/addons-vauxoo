from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    is_internal_transfer = fields.Boolean()

    @api.depends("partner_id", "company_id", "payment_type", "is_internal_transfer")
    def _compute_destination_account_id(self):
        internal_transfers = self.filtered("is_internal_transfer")
        for pay in internal_transfers:
            pay.destination_account_id = pay.company_id.transfer_account_id
        return super(AccountPayment, self - internal_transfers)._compute_destination_account_id()

    def action_draft(self):
        if self.env.context.get("skip_internal_transfer_pair_handling"):
            return super().action_draft()

        if len(self) == 1:
            paired = self.paired_internal_transfer_payment_id
            if self.is_internal_transfer and paired and paired.paired_internal_transfer_payment_id == self:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "internal.transfer.draft.confirm",
                    "view_mode": "form",
                    "target": "new",
                    "context": {
                        "default_payment_id": self.id,
                        "default_paired_payment_id": paired.id,
                    },
                }

        return super().action_draft()
