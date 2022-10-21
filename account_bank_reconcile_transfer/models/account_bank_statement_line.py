from odoo import models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def _prepare_reconciliation(self, lines_vals_list, allow_partial=False):
        """Inherit the method to create the internal transfers from the bank statement line.
        Note this method is run at the beginning of 'reconcile' method.
        """
        reconciliation_overview, open_balance_vals = super()._prepare_reconciliation(lines_vals_list, allow_partial)
        manual_payment_method = self.env.ref("account.account_payment_method_manual_out")
        for reconciliation in reconciliation_overview:
            line = reconciliation["line_vals"]
            if not line.get("transfer_journal_id"):
                continue
            statement = self.statement_id
            company = statement.company_id
            company.transfer_account_id = line["account_id"]
            statement_journal = statement.journal_id
            target_journal_id = line["transfer_journal_id"]
            is_credit = bool(line["credit"])
            transfer = self.env["account.payment"].create(
                {
                    "is_internal_transfer": True,
                    "payment_type": "inbound" if is_credit else "outbound",
                    "company_id": company.id,
                    "amount": line["credit"] if is_credit else line["debit"],
                    "currency_id": (self.currency_id or self.journal_id.currency_id or company.currency_id).id,
                    "date": self.date,
                    "ref": line.get("name") or "",
                    "journal_id": statement_journal.id,
                    "destination_journal_id": target_journal_id,
                    "payment_method_id": manual_payment_method.id,
                }
            )
            transfer.action_post()
            liquidity_lines, __counterpart_lines, __writeoff_lines = transfer._seek_for_lines()
            line["name"] = "%s: %s" % (transfer.name, liquidity_lines.name)
            line["account_id"] = liquidity_lines.account_id.id
            reconciliation["counterpart_line"] = liquidity_lines
            # This value is not needed anymore (This field does not belong to account.move.line)
            line.pop("transfer_journal_id")
        return reconciliation_overview, open_balance_vals
