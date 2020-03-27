from odoo import models, fields


class InternalTransferMulticurrency(models.TransientModel):
    _name = 'internal.transfer.multicurrency'
    _description = 'Wizard to modify the agreed amount with the bank on an internal transfer.'  # noqa

    partner_id = fields.Many2one('res.partner')
    agreed_amount = fields.Monetary(
        help="Agreed amount in the currency of the destination bank.")
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        default=lambda self: self._get_currency())

    def _get_currency(self):
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        if not active_ids or active_model != 'account.payment':
            return False
        payment = self.env['account.payment'].browse(active_ids)
        return (payment.destination_journal_id.currency_id or
                payment.company_id.currency_id)

    def apply(self):
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        if not active_ids or active_model != 'account.payment':
            return
        payment = self.env['account.payment'].browse(active_ids)
        payment.filtered(lambda p: p.state == 'draft').post()
        amls = self.env['account.move.line'].search([
            ('payment_id', '=', payment.id)])
        if self.partner_id:
            if len(amls) != 4:
                return
            amls.mapped('move_id').button_cancel()
            to_reconcile = amls.filtered(lambda x: x.full_reconcile_id)
            if amls.mapped('full_reconcile_id'):
                amls.remove_move_reconcile()
            amls.with_context(check_move_validity=False).write(
                {'partner_id': self.partner_id.id})
            to_reconcile.reconcile()
            amls.mapped('move_id').post()
            payment.write({'partner_id': self.partner_id.id})
        if (self.agreed_amount and
                self.currency_id == payment.company_id.currency_id):
            if len(amls) != 4:
                return
            amls.mapped('move_id').button_cancel()
            to_reconcile = amls.filtered(lambda x: x.full_reconcile_id)
            if amls.mapped('full_reconcile_id'):
                amls.remove_move_reconcile()
            debit = amls.filtered(lambda x: x.debit > 0)
            credit = amls.filtered(lambda x: x.credit > 0)
            debit.with_context(check_move_validity=False).write(
                {'debit': self.agreed_amount})
            aml_dest = debit.filtered(lambda x: x.move_id.journal_id.id == payment.destination_journal_id.id)
            aml_dest.with_context(check_move_validity=False).write(
                {'amount_currency': 0.00, 'currency_id': False})
            credit.with_context(check_move_validity=False).write(
                {'credit': self.agreed_amount})
            to_reconcile.reconcile()
            amls.mapped('move_id').post()
        elif (self.agreed_amount and
                self.currency_id != payment.company_id.currency_id):
            aml = amls.filtered(lambda a: a.amount_currency > 0.00)
            if len(aml) > 1:
                return
            aml.move_id.button_cancel()
            aml.with_context(check_move_validity=False).write(
                {'amount_currency': self.agreed_amount})
            aml.move_id.post()
