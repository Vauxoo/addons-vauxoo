from odoo import api, fields, models
from odoo.tools.translate import _


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    @api.onchange('percentage')
    def _onchange_amount_total(self):
        invoices = self.env['account.move'].browse(self._context.get('active_ids', self.active_id))
        self.amount_total = sum(invoices.mapped('amount_total')) * (self.percentage / 100)

    refund_method = fields.Selection(
        selection_add=[('early_payment', 'Early payment: Prepare a discount '
                                         'and reconcile automatically such '
                        'refund with the invoices selected')])
    percentage = fields.Float(default=5.0)
    product_id = fields.Many2one(
        'product.product', string='Product',
        default=lambda x: x.env.ref(
            'account_refund_early_payment.product_discount', False))
    amount_total = fields.Float()
    active_id = fields.Integer()

    def _prepare_default_reversal(self, move):
        result = super()._prepare_default_reversal(move)
        if self.refund_method != 'early_payment':
            return result
        reverse_date = self.date if self.date_mode == 'custom' else move.date
        return {
            'ref': _('Reversal of: %(move_name)s, %(reason)s', move_name=move.name, reason=self.reason)
                   if self.reason
                   else _('Reversal of: %s', move.name),
            'date': reverse_date,
            'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
            'journal_id': self.journal_id and self.journal_id.id or move.journal_id.id,
            'invoice_payment_term_id': None,
            'invoice_user_id': move.invoice_user_id.id,
            'auto_post': True if reverse_date > fields.Date.context_today(self) else False,
        }

    def reverse_moves(self):
        result = super().reverse_moves()
        if self.refund_method != 'early_payment':
            return result
        moves = self.move_ids
        total = sum(moves.mapped('amount_total'))
        refunds = self.new_move_ids
        refunds.invoice_line_ids = [(6, 0, [])]

        for inv, refund in zip_longest(moves, refunds, fillvalue=None):
            if not inv or not refund:
                break
            refund = refund.with_context(check_move_validity=False)
            percentage = inv.amount_total / total
            taxes = self.product_id.taxes_id
            tax_perc = sum(taxes.filtered(
                lambda tax: not tax.price_include
                and tax.amount_type == 'percent').mapped('amount'))
            account = self.product_id.product_tmpl_id.get_product_accounts(inv.fiscal_position_id)['income']
            invoice_line_ids = {
                'product_id': self.product_id.id,
                'name': self.product_id.name_get()[0][1],
                'product_uom_id': self.product_id.uom_id.id,
                'quantity': 1,
                'discount': 0,
                'tax_ids': taxes,
                'price_unit': self.amount_total * percentage / (1.0 + (tax_perc or 0.0) / 100),
                'account_id': account.id,
                'exclude_from_invoice_tab': False,
            }
            refund.write({'invoice_line_ids': [(0, 0, invoice_line_ids)]})
            refund.action_post()
            default_values_list = []
            for move in refund:
                default_values_list.append(self._prepare_default_reversal(move))

            batches = [
                [self.env['account.move'], [], True],   # Moves to be cancelled by the reverses.
                [self.env['account.move'], [], False],  # Others.
            ]
            for move, default_vals in zip(refund, default_values_list):
                is_auto_post = bool(default_vals.get('auto_post'))
                is_cancel_needed = not is_auto_post and self.refund_method in ('early_payment')
                batch_index = 0 if is_cancel_needed else 1
                batches[batch_index][0] |= move
                batches[batch_index][1].append(default_vals)

            # Handle reverse method.
            moves_to_redirect = self.env['account.move']
            for moves, default_values_list, is_cancel_needed in batches:
                new_moves = moves._reverse_moves(default_values_list, cancel=is_cancel_needed)

            moves_to_redirect |= new_moves
            self.new_move_ids = moves_to_redirect

        return result

    @api.model
    def action_split_reconcile(self, brw):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return False
        invoices = self.env['account.move'].browse(active_ids)
        prec = self.env['decimal.precision'].precision_get('Account')
        account_m_line_obj = self.env['account.move.line']

        brw.move_id.button_cancel()

        # we get the aml of refund to be split and reconciled
        to_reconcile_ids = {}
        for tmpline in brw.move_id.line_id:
            if (tmpline.account_id.reconcile
                    and tmpline.account_id.type == 'receivable'):
                move_line_id_refund = tmpline
                move_refund_credit = tmpline.credit
            elif tmpline.account_id.reconcile:
                to_reconcile_ids.setdefault(
                    tmpline.account_id.id, []).append(tmpline.id)

        amount_total_inv = 0
        invoice_source = []
        # Get the amount_total of all invoices to make
        # proration with refund

        for inv in invoices:
            amount_total_inv += inv.currency_id.round(inv.amount_total)
            invoice_source.append(inv.number)

        for inv in invoices:
            for line in inv.move_id.line_id:
                if (line.account_id.reconcile
                        and not line.reconcile_id
                        and line.account_id == move_line_id_refund.account_id):
                    amount_inv_refund = (
                        amount_total_inv and inv.amount_total
                        / amount_total_inv) * move_line_id_refund.credit or 0.0

                    if 1 > (abs(move_refund_credit - amount_inv_refund)) >\
                            10 ** (-max(5, prec)):
                        amount_inv_refund = move_refund_credit

                    move_line_id_inv_refund = move_line_id_refund.copy(
                        default={
                            'credit': inv.currency_id.round(
                                amount_inv_refund)})
                    move_refund_credit -= move_line_id_inv_refund.credit

                    line_to_reconcile = account_m_line_obj.browse(
                        [line.id, move_line_id_inv_refund.id])
                    line_to_reconcile.reconcile_partial()

                elif line.account_id.reconcile and not line.reconcile_id:
                    to_reconcile_ids.setdefault(
                        line.account_id.id, []).append(line.id)

        for account in to_reconcile_ids:
            if len(to_reconcile_ids[account]) > 1:
                line_to_reconcile_2 = account_m_line_obj.browse(
                    to_reconcile_ids[account])
                line_to_reconcile_2.reconcile_partial()

        move_line_id_refund.unlink()
        brw.move_id.action_post()
        brw.write(
            {'origin': ','.join(inv_source for inv_source in invoice_source)})
