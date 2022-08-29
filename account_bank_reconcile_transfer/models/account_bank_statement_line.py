from odoo import _, models
from odoo.exceptions import UserError


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def process_reconciliation(self, counterpart_aml_dicts=None, payment_aml_rec=None, new_aml_dicts=None):
        transfer_aml_dicts = [aml_dict for aml_dict in new_aml_dicts or [] if aml_dict.get("transfer_journal_id")]
        new_aml_dicts = [aml_dict for aml_dict in new_aml_dicts or [] if not aml_dict.get("transfer_journal_id")]
        counterpart_moves = super().process_reconciliation(
            counterpart_aml_dicts=counterpart_aml_dicts, payment_aml_rec=payment_aml_rec, new_aml_dicts=new_aml_dicts
        )
        payment_model = self.env["account.payment"]
        manual_payment_method = self.env.ref("account.account_payment_method_manual_out")
        for transfer_dict in transfer_aml_dicts:
            statement = self.statement_id
            company = statement.company_id
            original_transfer_account = company.transfer_account_id
            company.transfer_account_id = transfer_dict["account_id"]
            statement_journal = statement.journal_id
            target_journal_id = transfer_dict["transfer_journal_id"]
            is_credit = bool(transfer_dict["credit"])
            transfer = payment_model.create(
                {
                    "payment_type": "transfer",
                    "company_id": company.id,
                    "amount": transfer_dict["credit"] if is_credit else transfer_dict["debit"],
                    "currency_id": (self.currency_id or self.journal_id.currency_id or company.currency_id).id,
                    "payment_date": self.date,
                    "communication": transfer_dict.get("name") or "",
                    "journal_id": target_journal_id if is_credit else statement_journal.id,
                    "destination_journal_id": statement_journal.id if is_credit else target_journal_id,
                    "payment_method_id": manual_payment_method.id,
                }
            )
            transfer.post()
            account = statement_journal["default_%s_account_id" % ("debit" if is_credit else "credit")]
            move_line = transfer.move_line_ids.filtered(
                lambda move: move.account_id == account and (move.debit if is_credit else move.credit)
            )
            if len(move_line) != 1:
                raise UserError(
                    _("Could not identify the correct transfer move. Make sure bank journals are properly set up.")
                )
            move_line.statement_line_id = self.id
            move = move_line.move_id
            counterpart_moves += move
            company.transfer_account_id = original_transfer_account
        return counterpart_moves
