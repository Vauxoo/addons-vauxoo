from odoo import api, fields, models
from odoo.exceptions import UserError


class InternalTransferMulticurrency(models.TransientModel):
    _name = "internal.transfer.multicurrency"
    _description = "Wizard to create an internal transfer with an agreed amount."

    company_id = fields.Many2one(
        "res.company",
        required=True,
    )
    company_currency_id = fields.Many2one(
        related="company_id.currency_id",
    )
    date = fields.Date(
        required=True,
        default=fields.Date.today,
    )
    memo = fields.Char()

    # Sending Transaction
    out_journal_id = fields.Many2one(
        "account.journal",
        required=True,
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]",
    )
    out_currency_id = fields.Many2one(
        "res.currency",
    )
    out_currency_locked = fields.Boolean(compute="_compute_out_currency_locked")
    out_amount_currency = fields.Monetary(
        currency_field="out_currency_id",
        required=True,
    )
    out_amount = fields.Monetary(
        currency_field="company_currency_id",
        required=True,
    )
    out_payment_method_line_id = fields.Many2one(
        "account.payment.method.line",
        compute="_compute_out_payment_method_line_id",
        readonly=False,
        domain="[('journal_id', '=', out_journal_id), ('payment_type', '=', 'outbound'), ('payment_account_id', '!=', False)]",
    )

    # Receiving Transaction
    in_journal_id = fields.Many2one(
        "account.journal",
        required=True,
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id), ('id', '!=', out_journal_id)]",
    )
    in_currency_id = fields.Many2one(
        "res.currency",
    )
    in_currency_locked = fields.Boolean(compute="_compute_in_currency_locked")
    in_amount_currency = fields.Monetary(
        currency_field="in_currency_id",
        required=True,
    )
    in_amount = fields.Monetary(
        currency_field="company_currency_id",
        compute="_compute_in_amount",
    )
    in_payment_method_line_id = fields.Many2one(
        "account.payment.method.line",
        compute="_compute_in_payment_method_line_id",
        readonly=False,
        domain="[('journal_id', '=', in_journal_id), ('payment_type', '=', 'inbound'), ('payment_account_id', '!=', False)]",
    )

    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        journal = self.env["account.journal"].browse(self.env.context["default_journal_id"])
        res["company_id"] = journal.company_id.id
        res["out_journal_id"] = journal.id
        res["out_currency_id"] = (journal.currency_id or journal.company_id.currency_id).id
        return res

    @api.depends("out_journal_id")
    def _compute_out_currency_locked(self):
        for rec in self:
            rec.out_currency_locked = bool(rec.out_journal_id.currency_id)

    @api.depends("in_journal_id")
    def _compute_in_currency_locked(self):
        for rec in self:
            rec.in_currency_locked = bool(rec.in_journal_id.currency_id)

    @api.onchange("out_journal_id", "company_id")
    def _onchange_out_currency_id(self):
        self.out_currency_id = self.out_journal_id.currency_id or self.company_id.currency_id

    @api.onchange("in_journal_id", "company_id")
    def _onchange_in_currency_id(self):
        self.in_currency_id = self.in_journal_id.currency_id or self.company_id.currency_id

    @api.onchange("out_amount_currency", "out_currency_id", "date")
    def _onchange_out_amount(self):
        if not (self.out_currency_id and self.out_amount_currency and self.company_currency_id):
            return
        if self.out_currency_id == self.company_currency_id:
            self.out_amount = self.out_amount_currency
        else:
            self.out_amount = self.out_currency_id._convert(
                self.out_amount_currency,
                self.company_currency_id,
                self.company_id,
                self.date or fields.Date.today(),
            )

    @api.onchange("in_journal_id", "in_currency_id", "out_amount")
    def _onchange_in_amount_currency(self):
        if self.in_currency_id and self.company_currency_id and self.in_currency_id == self.company_currency_id:
            self.in_amount_currency = self.out_amount

    @api.depends("out_amount")
    def _compute_in_amount(self):
        for rec in self:
            rec.in_amount = rec.out_amount

    @api.depends("out_journal_id")
    def _compute_out_payment_method_line_id(self):
        for rec in self:
            valid = rec.out_journal_id.outbound_payment_method_line_ids.filtered(lambda line: line.payment_account_id)
            rec.out_payment_method_line_id = valid[:1]

    @api.depends("in_journal_id")
    def _compute_in_payment_method_line_id(self):
        for rec in self:
            valid = rec.in_journal_id.inbound_payment_method_line_ids.filtered(lambda line: line.payment_account_id)
            rec.in_payment_method_line_id = valid[:1]

    # ADR2
    @api.constrains("out_journal_id", "in_journal_id")
    def _check_different_journals(self):
        for rec in self:
            if rec.out_journal_id and rec.out_journal_id == rec.in_journal_id:
                raise UserError(self.env._("The source and destination journals must be different."))

    # ADR4
    @api.constrains("out_journal_id", "in_journal_id", "company_id")
    def _check_same_company(self):
        for rec in self:
            if rec.out_journal_id and rec.out_journal_id.company_id != rec.company_id:
                raise UserError(
                    self.env._(
                        'Journal "%s" does not belong to company "%s".',
                        rec.out_journal_id.display_name,
                        rec.company_id.display_name,
                    )
                )
            if rec.in_journal_id and rec.in_journal_id.company_id != rec.company_id:
                raise UserError(
                    self.env._(
                        'Journal "%s" does not belong to company "%s".',
                        rec.in_journal_id.display_name,
                        rec.company_id.display_name,
                    )
                )

    # ADR3
    @api.constrains(
        "out_journal_id",
        "in_journal_id",
        "out_currency_id",
        "in_currency_id",
        "out_amount_currency",
        "in_amount_currency",
    )
    def _check_same_currency_amounts(self):
        for rec in self:
            out_currency = rec.out_journal_id.currency_id or rec.out_currency_id or rec.company_currency_id
            in_currency = rec.in_journal_id.currency_id or rec.in_currency_id or rec.company_currency_id
            if (
                out_currency
                and out_currency == in_currency
                and out_currency.compare_amounts(rec.out_amount_currency, rec.in_amount_currency)
            ):
                raise UserError(
                    self.env._(
                        "When both journals use the same currency (%s), "
                        "the sent and received amounts must be equal.",
                        out_currency.name,
                    )
                )

    # ADR5 — sending side
    @api.constrains("out_journal_id", "out_currency_id", "out_amount_currency", "out_amount")
    def _check_out_local_amount(self):
        for rec in self:
            out_currency = rec.out_journal_id.currency_id or rec.out_currency_id or rec.company_currency_id
            if (
                out_currency
                and rec.company_currency_id
                and out_currency == rec.company_currency_id
                and rec.company_currency_id.compare_amounts(rec.out_amount_currency, rec.out_amount)
            ):
                raise UserError(
                    self.env._(
                        "The source journal uses the company currency (%s). "
                        "The sent amount and the local amount must be equal.",
                        rec.company_currency_id.name,
                    )
                )

    # ADR5 — receiving side
    @api.constrains("in_journal_id", "in_currency_id", "in_amount_currency", "out_amount")
    def _check_in_local_amount(self):
        for rec in self:
            in_currency = rec.in_journal_id.currency_id or rec.in_currency_id or rec.company_currency_id
            if (
                in_currency
                and rec.company_currency_id
                and in_currency == rec.company_currency_id
                and rec.company_currency_id.compare_amounts(rec.in_amount_currency, rec.out_amount)
            ):
                raise UserError(
                    self.env._(
                        "The destination journal uses the company currency (%s). "
                        "The received amount and the local amount must be equal.",
                        rec.company_currency_id.name,
                    )
                )

    # ADR6
    @api.constrains("out_journal_id", "in_journal_id")
    def _check_payment_method_accounts(self):
        for rec in self:
            if rec.out_payment_method_line_id and not rec.out_payment_method_line_id.payment_account_id:
                raise UserError(self.env._("The outbound payment method must have an account configured."))
            if rec.in_payment_method_line_id and not rec.in_payment_method_line_id.payment_account_id:
                raise UserError(self.env._("The inbound payment method must have an account configured."))
            if (
                rec.out_payment_method_line_id
                and rec.in_payment_method_line_id
                and rec.out_payment_method_line_id.payment_account_id
                == rec.in_payment_method_line_id.payment_account_id
            ):
                raise UserError(
                    self.env._("The payment accounts for the outbound and inbound methods must be different.")
                )

    def _validate_before_create(self):
        self.ensure_one()
        if not self.company_id.transfer_account_id:
            raise UserError(
                self.env._(
                    'Company "%s" does not have an internal transfer account configured.',
                    self.company_id.display_name,
                )
            )
        if not self.out_payment_method_line_id:
            raise UserError(self.env._("Please select an outbound payment method."))
        if not self.in_payment_method_line_id:
            raise UserError(self.env._("Please select an inbound payment method."))
        if not self.out_payment_method_line_id.payment_account_id:
            raise UserError(self.env._("The outbound payment method must have an account configured."))
        if not self.in_payment_method_line_id.payment_account_id:
            raise UserError(self.env._("The inbound payment method must have an account configured."))
        if self.out_payment_method_line_id.payment_account_id == self.in_payment_method_line_id.payment_account_id:
            raise UserError(self.env._("The payment accounts for the outbound and inbound methods must be different."))

    def action_create_internal_transfer(self):
        self._validate_before_create()

        common_vals = {
            "company_id": self.company_id.id,
            "date": self.date,
            "partner_type": "customer",
            "is_internal_transfer": True,
            "memo": self.memo or "",
        }

        out_currency = self.out_journal_id.currency_id or self.out_currency_id or self.company_id.currency_id
        in_currency = self.in_journal_id.currency_id or self.in_currency_id or self.company_id.currency_id

        out_payment = self.env["account.payment"].create(
            {
                **common_vals,
                "journal_id": self.out_journal_id.id,
                "currency_id": out_currency.id,
                "amount": self.out_amount_currency,
                "payment_type": "outbound",
                "payment_method_line_id": self.out_payment_method_line_id.id,
            }
        )

        in_payment = self.env["account.payment"].create(
            {
                **common_vals,
                "journal_id": self.in_journal_id.id,
                "currency_id": in_currency.id,
                "amount": self.in_amount_currency,
                "payment_type": "inbound",
                "payment_method_line_id": self.in_payment_method_line_id.id,
            }
        )

        out_payment.paired_internal_transfer_payment_id = in_payment
        in_payment.paired_internal_transfer_payment_id = out_payment

        (out_payment | in_payment).action_post()

        # ORM-level writes after action_post() trigger _synchronize_to_moves() (via stored
        # computed field recomputes that lose the skip context), which resets the balance to
        # the FX-rate value. Write directly via SQL to bypass all ORM hooks.
        local = self.company_currency_id.round(self.out_amount)
        for payment in (out_payment, in_payment):
            for line in payment.move_id.line_ids:
                if line.amount_currency >= 0:
                    self.env.cr.execute(
                        "UPDATE account_move_line"
                        " SET debit = %s, credit = 0, balance = %s, amount_residual = %s"
                        " WHERE id = %s",
                        (local, local, local, line.id),
                    )
                else:
                    self.env.cr.execute(
                        "UPDATE account_move_line"
                        " SET debit = 0, credit = %s, balance = -%s, amount_residual = -%s"
                        " WHERE id = %s",
                        (local, local, local, line.id),
                    )
        # flush=False: do NOT let the ORM flush its cached (FX-rate) field values back to DB
        # before clearing the cache — those cached values would overwrite our SQL bypass.
        self.env["account.move.line"].invalidate_model(["debit", "credit", "balance", "amount_residual"], flush=False)

        # Reconcile the two transfer account lines so the transit account is cleared.
        # Odoo falls back to company currency (MXN) when the two lines are in different
        # foreign currencies, so the reconciliation is clean with no exchange difference.
        transfer_account = self.company_id.transfer_account_id
        if not transfer_account.reconcile:
            transfer_account.reconcile = True
        out_transfer_line = out_payment.move_id.line_ids.filtered(lambda line: line.account_id == transfer_account)
        in_transfer_line = in_payment.move_id.line_ids.filtered(lambda line: line.account_id == transfer_account)
        (out_transfer_line | in_transfer_line).reconcile()

        out_payment.message_post(body=self.env._("A second payment has been created: %s", in_payment._get_html_link()))
        in_payment.message_post(body=self.env._("This payment has been created from %s", out_payment._get_html_link()))

        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Internal Transfer Payments"),
            "res_model": "account.payment",
            "view_mode": "list,form",
            "views": [
                (self.env.ref("account.view_account_payment_tree").id, "list"),
                (False, "form"),
            ],
            "domain": [("id", "in", [out_payment.id, in_payment.id])],
            "target": "current",
        }
