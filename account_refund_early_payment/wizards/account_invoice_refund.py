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
                        'refund with the invoices selected')], ondelete={"early_payment": "cascade"})
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
        total = move.amount_untaxed * (self.percentage / 100)
        new_line = move.invoice_line_ids.new(origin=move.invoice_line_ids[:1])
        new_line.update({'product_id': self.product_id.id})
        new_line._onchange_product_id()
        new_line.update({'quantity': 1, 'price_unit': total})
        new_line._onchange_price_subtotal()
        line_vals = new_line._convert_to_write(new_line._cache)
        move_vals = move.copy_data(default=result)[0]
        move_vals['invoice_line_ids'] = [(0, 0, line_vals)]
        move_vals.pop('line_ids')
        values = move._move_autocomplete_invoice_lines_create([move_vals])[0]
        values['line_ids'] = [line for line in values['line_ids'] if line[0] != 6]
        values['invoice_origin'] = move.name
        return values

    def reverse_moves(self):
        if self.refund_method != 'early_payment':
            return super().reverse_moves()
        moves = self.move_ids
        default_values_list = []
        for move in moves:
            default_values_list.append(self._prepare_default_reversal(move))

        batches = [
            [self.env['account.move'], [], True],   # Moves to be cancelled by the reverses.
            [self.env['account.move'], [], False],  # Others.
        ]
        for move, default_vals in zip(moves, default_values_list):
            is_auto_post = bool(default_vals.get('auto_post'))
            is_cancel_needed = not is_auto_post

            batch_index = 0 if is_cancel_needed else 1
            batches[batch_index][0] |= move
            batches[batch_index][1].append(default_vals)

        # Handle reverse method.
        moves_to_redirect = self.env['account.move']
        for moves, default_values_list, is_cancel_needed in batches:
            new_moves = moves._reverse_moves(default_values_list, cancel=is_cancel_needed)
            moves_to_redirect |= new_moves
        self.new_move_ids = moves_to_redirect

        # Create action.
        action = {
            'name': _('Reverse Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
        }
        if len(moves_to_redirect) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': moves_to_redirect.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', moves_to_redirect.ids)],
            })
        return action
