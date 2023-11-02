from odoo import _, fields, models
from odoo.exceptions import ValidationError


class InternalTransferMulticurrency(models.TransientModel):
    _name = "internal.transfer.multicurrency"
    _description = "Wizard to modify the agreed amount with the bank on an internal transfer."  # noqa

    agreed_amount = fields.Monetary(help="Agreed amount in the currency of the destination bank.")
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self._get_currency(),
    )

    def _get_currency(self):
        active_ids = self._context.get("active_ids")
        active_model = self._context.get("active_model")
        if not active_ids or active_model != "account.payment":
            return False
        payment = self.env["account.payment"].browse(active_ids)
        return payment.destination_journal_id.currency_id or payment.company_currency_id

    def _get_currencies(self, payment):
        payment_currency = payment.currency_id
        company_currency = payment.company_currency_id
        send_currency = payment.journal_id.currency_id or company_currency
        receive_currency = self.currency_id
        currencies = payment_currency | company_currency | send_currency | receive_currency
        return currencies

    def _validate_currencies_in_internal_transfer(self, payment):
        currencies = self._get_currencies(payment)
        if len(currencies) == 2:
            return currencies - payment.currency_id
        raise ValidationError(
            _(
                "Agreed amount is available when there are two considered currencies. "
                "Currently, the following currencies are being considered:\n- %s",
                "\n- ".join(currencies.mapped("name")),
            )
        )

    def _prepare_values_from_lines(self, lines, currency=None, is_same_company_currency=False):
        line = lines[0]
        if is_same_company_currency:
            return {"debit": self.agreed_amount} if line.debit > 0 else {"credit": self.agreed_amount}
        vals = {"debit": line.debit} if line.amount_currency > 0 else {"credit": line.credit}
        sign = 1 if line.amount_currency > 0 else -1
        vals.update({"amount_currency": sign * self.agreed_amount, "currency_id": currency.id})
        return vals

    def _preprocess_payments_hooks(self, payment):
        """This method is to be inherited in case pre-processing is required on the payments."""
        return payment

    def _postprocess_payments_hooks(self, payment):
        """This method is to be inherited in case post-processing is required on the payments."""
        return payment

    def apply(self):
        active_ids = self._context.get("active_ids")
        active_model = self._context.get("active_model")
        if not active_ids or active_model != "account.payment":
            return
        payment = self.env["account.payment"].browse(active_ids)
        exchange_currency = self._validate_currencies_in_internal_transfer(payment)
        payment.filtered(lambda p: p.state == "draft").action_post()
        amls = (payment | payment.paired_internal_transfer_payment_id).line_ids
        if not self.agreed_amount:
            return
        to_reconcile = amls.filtered(
            lambda l: l.account_id == l.company_id.transfer_account_id
        ).full_reconcile_id.reconciled_line_ids
        context = {"check_move_validity": False, "skip_account_move_synchronization": True}
        if exchange_currency == payment.company_currency_id:
            if len(amls) != 4:
                return
            amls.move_id.button_draft()
            self._preprocess_payments_hooks(payment)
            debit = amls.filtered(lambda x: x.debit > 0)
            credit = amls.filtered(lambda x: x.credit > 0)
            vals = self._prepare_values_from_lines(debit, is_same_company_currency=True)
            debit.with_context(**context).write(vals)
            vals = self._prepare_values_from_lines(credit, is_same_company_currency=True)
            credit.with_context(**context).write(vals)
            self._postprocess_payments_hooks(payment)
            amls.move_id.action_post()
            to_reconcile.reconcile()
            return
        aml_positive = amls.filtered(lambda a: a.amount_currency > 0.00)
        aml_negative = amls.filtered(lambda a: a.amount_currency < 0.00)
        if len(aml_positive) > 2 or len(aml_negative) > 2:
            return
        aml_positive.move_id.button_draft()
        self._preprocess_payments_hooks(payment)
        vals = self._prepare_values_from_lines(aml_positive, exchange_currency)
        aml_positive.with_context(**context).write(vals)
        vals = self._prepare_values_from_lines(aml_negative, exchange_currency)
        aml_negative.with_context(**context).write(vals)
        self._postprocess_payments_hooks(payment)
        aml_positive.move_id.action_post()
        to_reconcile.reconcile()
