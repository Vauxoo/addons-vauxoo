# Copyright 2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountInvoiceSplit(models.TransientModel):
    _name = "account.invoice.split"
    _description = "Invoice Splitter"

    invoice_id = fields.Many2one('account.invoice', String="Invoice to Split")
    new_invoice_id = fields.Many2one('account.invoice')
    percent = fields.Float(
        string="Percent to Pay",
        help="Percent of the amount that will be paid on the current invoice")
    create_invoice = fields.Boolean(
        string="Create New Invoice", default=True,
        help="Specifies whether a new invoice will be created in draft mode "
        "with the remaining uncovered amount")

    @api.model
    def default_get(self, fields_list):
        """Ensure only invoices in draft may be split"""
        res_ids = self._context.get('active_ids')
        invoices = self.env['account.invoice'].browse(res_ids)
        inv_not_draft = invoices.filtered(lambda inv: inv.state != 'draft')
        if inv_not_draft:
            raise UserError(_(
                "You may split invoices only when they are in draft mode."))
        return super(AccountInvoiceSplit, self).default_get(fields_list)

    @api.multi
    def action_split_invoice(self):
        """Actual action called by the wizard once it's fulfilled

        When invoices are split, their lines are copied and product quantities
        are divided which may produce non-integer quantities. This process is
        done without taking into account unit of measures. That means, if a
        line contains, for instance, three shirts, and the invoice is split to
        50%; then the invoice will be for 1.5 shirts after the invoice is
        split, even though that is not possible in practice.
        """
        valid_percent = 0 < self.percent < 100
        if not valid_percent:
            raise UserError(_(
                "Invalid percent %s%%.\n\n"
                "It must be a number greater than 0 and less than 100.") % (
                    self.percent))
        if self.create_invoice:
            self.new_invoice_id = self.invoice_id.copy()
            for line in self.new_invoice_id.invoice_line_ids:
                line.quantity *= (100-self.percent)/100
            self.new_invoice_id.compute_taxes()
        for line in self.invoice_id.invoice_line_ids:
            line.quantity *= self.percent/100
        self.invoice_id.compute_taxes()
        return self.action_open_invoices()

    @api.multi
    def action_open_invoices(self):
        """Action to be executed once invoice is split

        There are two possibilities:
        - If no new invoice was created, current invoice is refreshed
        - If it was created, a list view is opened, listing both current and
          new invoices
        """
        self.ensure_one()
        invoices = self.invoice_id + self.new_invoice_id
        return {
            'name': _('Split Invoice'),
            'view_type': 'form',
            'view_mode': 'tree,form' if self.new_invoice_id else 'form',
            'res_model': 'account.invoice',
            'res_id': invoices.ids[0],
            'domain': [('id', 'in', invoices.ids)],
            'type': 'ir.actions.act_window',
            'context': {'type': 'out_invoice'},
        }
