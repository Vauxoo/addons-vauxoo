# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
# ############ Credits ########################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Audited by: Jose Morales <jose@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp import fields, api, models


class AccountInvoiceRefund(models.TransientModel):
    """Refunds invoice"""

    _inherit = "account.invoice.refund"

    @api.model
    def _search_xml_id(self):
        res_id = False
        imd_id = self.env.ref(
            'account_refund_early_payment.product_discount_early_payment')
        if imd_id:
            res_id = imd_id.id
        return res_id

    @api.multi
    def _compute_amount(
            self, field_names, arg=None, context=None,
            query='', query_params=()):
        if context is None:
            context = {}
        res = {}
        for wzd in self.browse():
            res[wzd.id] = wzd.percent * 10

        return res

    @api.multi
    def onchange_amount_total(self, percent=0.0, active_id=None, context=None):
        context = dict(self._context)
        inv_obj = self.env['account.invoice']
        amount_total = 0
        for inv in inv_obj.browse(context.get('active_ids', active_id)):
            amount_total += inv.amount_total * (percent / 100)
        return {
            'value': {
                'amount_total': amount_total
            }
        }

    @api.model
    def _get_percent_default(self):
        """
        It is a hook method. In order to put some smart computation.
        """
        return 5.0

    filter_refund = fields.\
        Selection(selection_add=[('early_payment',
                                  'Early payment: Discount early payment')])
    percent = fields.Float('Percent', default=_get_percent_default)
    product_id = fields.Many2one(
        'product.product', string='Product', default=_search_xml_id)
    amount_total = fields.Float('Amount')
    active_id = fields.Integer('Active ID')

    @api.multi
    def compute_refund(self, mode):
        context = dict(self._context)
        if mode == 'early_payment':
            ctx = context.copy()
            context.update(
                {'active_ids': context.get('active_ids')[0]})

        result = super(
            AccountInvoiceRefund, self.with_context(context)).compute_refund(
                mode)

        if mode != 'early_payment':
            return result

        inv_obj = self.env['account.invoice']
        at_obj = self.env['account.tax']
        inv_line_obj = self.env['account.invoice.line']

        refund_id = result.get('domain')[1][2]

        amount_total = self.amount_total
        prod_brw = self.product_id
        for inv in inv_obj.browse(ctx.get('active_ids')):
            brw = inv_obj.browse(refund_id)

            if not brw.invoice_line:
                continue

            for rl in brw.invoice_line:
                rl.unlink()

            fp = inv.fiscal_position and inv.fiscal_position.id
            data = inv_line_obj.product_id_change(
                prod_brw.id,
                prod_brw.uom_id.id,
                1.0,
                prod_brw.name,
                inv.type,
                inv.partner_id.id,
                fp,
                amount_total,
                inv.currency_id.id,
                inv.company_id.id
                )

            if 'value' not in data and data['value']:
                continue
            perc = 0.0
            if data['value'].get('invoice_line_tax_id'):

                tax_ids = data['value']['invoice_line_tax_id']
                data['value']['invoice_line_tax_id'] = [(6, 0, tax_ids)]
                for tax_brw in at_obj.browse(tax_ids):
                    perc += tax_brw.amount
            data['value']['product_id'] = prod_brw.id
            data['value']['quantity'] = 1.0
            data['value']['price_unit'] = amount_total / (1.0 + abs(perc))
            data['value']['invoice_id'] = refund_id[0]
            inv_line_obj.create(data['value'])

            brw.button_reset_taxes()
            brw.signal_workflow('invoice_open')

        self.action_split_reconcile(brw)

        return result

    @api.model
    def action_split_reconcile(self, brw):

        context = dict(self._context)
        prec = self.env['decimal.precision'].precision_get('Account')
        inv_obj = self.env['account.invoice']
        account_m_line_obj = self.env['account.move.line']

        brw.move_id.button_cancel()

        # we get the aml of refund to be split and reconciled
        to_reconcile_ids = {}
        for tmpline in brw.move_id.line_id:
            if tmpline.account_id.reconcile and\
                    tmpline.account_id.type in ('receivable'):
                move_line_id_refund = tmpline
                move_refund_credit = tmpline.credit
            elif tmpline.account_id.reconcile:
                to_reconcile_ids.setdefault(
                    tmpline.account_id.id, []).append(tmpline.id)

        amount_total_inv = 0
        invoice_source = []
        # Get the amount_total of all invoices to can make
        # proration with refund

        for inv in inv_obj.browse(context.get('active_ids')):
            amount_total_inv += inv.currency_id.round(inv.amount_total)
            invoice_source.append(inv.number)

        for inv in inv_obj.browse(context.get('active_ids')):
            for line in inv.move_id.line_id:
                if line.account_id.reconcile and not\
                        line.reconcile_id and\
                        line.account_id == move_line_id_refund.account_id:
                    amount_inv_refund = (
                        amount_total_inv and inv.amount_total / amount_total_inv) *\
                        move_line_id_refund.credit or 0.0

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
        brw.move_id.button_validate()
        brw.write(
            {'origin': ','.join(inv_source for inv_source in invoice_source)})
