# coding: utf-8

from itertools import zip_longest
from odoo import api, fields, models


class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    @api.onchange('percentage')
    def _onchange_amount_total(self):
        inv_obj = self.env['account.invoice']
        invoices = inv_obj.browse(
            self._context.get('active_ids', self.active_id))
        amount_total = sum(
            invoices.mapped('amount_total')) * self.percentage / 100
        self.amount_total = amount_total

    filter_refund = fields.Selection(
        selection_add=[('early_payment', 'Early payment: Prepare a discount '
                                         'and reconcile automatically such '
                                         'refund with the invoices selected')])
    percentage = fields.Float(default=5.0)
    product_id = fields.Many2one(
        'product.product', string='Product',
        default=lambda x: x.env.ref(
            'account_refund_early_payment.product_discount'))
    amount_total = fields.Float()
    active_id = fields.Integer()

    @api.multi
    def compute_refund(self, mode):
        result = super(AccountInvoiceRefund, self).compute_refund(mode)
        if mode != 'early_payment':
            return result
        invoices = self.env['account.invoice'].browse(
            self._context.get('active_ids'))
        total = sum(invoices.mapped('amount_total'))
        refunds = invoices.browse(result.get('domain')[1][2])
        refunds.mapped('invoice_line_ids').unlink()
        for inv, refund in zip_longest(invoices, refunds, fillvalue=None):
            if not inv or not refund:
                break
            product = self.product_id
            percentage = inv.amount_total / total
            taxes = product.taxes_id
            tax_perc = sum(taxes.filtered(
                lambda tax: not tax.price_include
                and tax.amount_type == 'percent').mapped('amount'))
            account_id = (product.property_account_income_id.id or
                          product.categ_id.property_account_income_categ_id.id)
            self.env['account.invoice.line'].create({
                'invoice_id': refund.id,
                'product_id': product.id,
                'name': product.name_get()[0][1],
                'uom_id': product.uom_id.id,
                'invoice_line_tax_ids': [
                    (6, 0, taxes._ids)],
                'price_unit': self.amount_total * percentage / (
                    1.0 + (tax_perc or 0.0) / 100),
                'account_id': account_id,
            })
            refund.compute_taxes()
            refund.action_invoice_open()
            # Which is the aml to reconcile to (the receivable one)
            reconcile = refund.move_id.line_ids.filtered(
                lambda x: x.account_id == refund.account_id).sorted(
                'date_maturity')
            inv.assign_outstanding_credit(reconcile.id)
        return result
