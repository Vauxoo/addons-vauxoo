# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Ernesto García Medina (ernesto_gm@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    invoice_broker_id = fields.Many2one(
        'account.invoice', 'Overseas Invoice', help='If this invoice line is '
        'to the payment to a broker, indicate the original invoice that must '
        'be generated the broker partner',
        domain=[('type', '=', 'in_invoice')])
    partner_broker_ok = fields.Boolean(
        string='Partner Broker', related='invoice_id.partner_id.is_broker_ok',
        store=False, readonly=True,
        help='Indicate if the partner to invoice is broker')


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    tax_partner_id = fields.Many2one('res.partner', 'Supplier', readonly=True)

    @api.v8
    def compute_broker(self, invoice):
        """Super to this method, to calculate values to taxes from lines that your
        quantity is 0, and have invoice_broker_id.
        """
        currency = invoice.currency_id.with_context(
            date=invoice.date_invoice or
            fields.Date.context_today(invoice))
        company_currency = invoice.company_id.currency_id
        res = self.compute(invoice)
        tax_by_partner = {}
        for line in invoice.invoice_line:
            if line.invoice_broker_id and line.quantity == 0 and\
                    line.partner_broker_ok:
                taxes = line.invoice_line_tax_id.compute_all(
                    (line.price_unit * (1 - (line.discount or 0.0) / 100.0)),
                    1.0, line.product_id, invoice.partner_id)['taxes']
                partner_l_id = line.invoice_broker_id.partner_id.id
                for tax in taxes:
                    base = currency.round(tax.get('price_unit', 0.0))
                    amount = tax.get('amount', 0.0)
                    if invoice.type in ('out_invoice', 'in_invoice'):
                        tx_bs_am = currency.compute(base * tax.get(
                            'base_sign', 0.0), company_currency, round=False)
                        tx_am = currency.compute(
                            tax.get('amount', 0.0) * tax.get('tax_sign', 0.0),
                            company_currency, round=False)
                        base_code_id = tax.get('base_code_id', False)
                        tax_code_id = tax.get('tax_code_id', False)
                        account_id = tax.get(
                            'account_collected_id', line.account_id.id)
                        account_analytic_id = tax.get(
                            'account_analytic_collected_id', False)
                    else:
                        tx_bs_am = currency.compute(
                            base * tax.get('ref_base_sign', 0.0),
                            company_currency, round=False)
                        tx_am = currency.compute(
                            tax.get('amount', 0.0) * tax.get(
                                'ref_tax_sign', 0.0), company_currency,
                            round=False)
                        base_code_id = tax.get('ref_base_code_id', False)
                        tax_code_id = tax.get('ref_tax_code_id', False)
                        account_id = tax.get(
                            'account_paid_id', line.account_id.id)
                        account_analytic_id = tax.get(
                            'account_analytic_paid_id', False)

                    if tax.get('id', False) in tax_by_partner:
                        if partner_l_id in tax_by_partner.get(tax.get('id')):
                            tax_by_partner.get(
                                tax.get('id')).get(partner_l_id).update({
                                    'base': tax_by_partner.get(
                                        tax.get('id')).get(partner_l_id).get(
                                            'base', 0.0) + base,
                                    'amount': tax_by_partner.get(
                                        tax.get('id')).get(partner_l_id).get(
                                            'amount', 0.0) + amount,
                                    'base_amount': tax_by_partner.get(
                                        tax.get('id')).get(partner_l_id).get(
                                            'base_amount', 0.0) + tx_bs_am,
                                    'tax_amount': tax_by_partner.get(
                                        tax.get('id')).get(partner_l_id).get(
                                            'tax_amount', 0.0) + tx_am
                                })
                        else:
                            tax_by_partner.get(tax.get('id')).update({
                                partner_l_id: {
                                    'base': base,
                                    'amount': amount,
                                    'base_amount': tx_bs_am,
                                    'tax_amount': tx_am,
                                    'base_code_id': base_code_id,
                                    'tax_code_id': tax_code_id,
                                    'account_id': account_id,
                                    'account_analytic_id': account_analytic_id,
                                    'invoice_id': invoice.id,
                                    'name': tax.get('name', ''),
                                    'manual': False,
                                    'sequence': tax.get('sequence', False),
                                    'tax_id': tax.get('id'),
                                    'tax_partner_id': partner_l_id
                                }
                            })
                    else:
                        tax_by_partner.update({
                            tax.get('id'): {
                                partner_l_id: {
                                    'base': base,
                                    'amount': amount,
                                    'base_amount': tx_bs_am,
                                    'tax_amount': tx_am,
                                    'base_code_id': base_code_id,
                                    'tax_code_id': tax_code_id,
                                    'account_id': account_id,
                                    'account_analytic_id': account_analytic_id,
                                    'invoice_id': invoice.id,
                                    'name': tax.get('name', ''),
                                    'manual': False,
                                    'sequence': tax.get('sequence', False),
                                    'tax_id': tax.get('id'),
                                    'tax_partner_id': partner_l_id
                                }
                            }
                        })
        for tax in res:
            if tax not in tax_by_partner:
                tax_by_partner.update({
                    tax: {
                        invoice.partner_id.id: res.get(tax)}})
        for tax in tax_by_partner:
            res.update({tax: tax_by_partner.get(tax)})
        return res

    def move_line_get(self, cr, uid, invoice_id, context=None):
        """Super to function, to add partner_id in dict, this to create the
        line corresponding to tax with the partner to this, this when the
        line of tax is to register cost of to broker
        """
        res = []
        super(AccountInvoiceTax, self).move_line_get(cr, uid, invoice_id)
        tax_invoice_ids = self.search(cr, uid, [
            ('invoice_id', '=', invoice_id)], context=context)
        for inv_t in self.browse(cr, uid, tax_invoice_ids, context=context):
            if not inv_t.base_amount and not inv_t.tax_code_id and not\
                    inv_t.tax_amount:
                continue
            res.append({
                'type': 'tax',
                'name': inv_t.name,
                'price_unit': inv_t.amount,
                'quantity': 1,
                'price': inv_t.amount or 0.0,
                'account_id': inv_t.account_id.id or False,
                'tax_code_id': inv_t.tax_code_id.id or False,
                'tax_amount': inv_t.tax_amount or False,
                'account_analytic_id': inv_t.account_analytic_id.id or False,
                'amount_base': abs(inv_t.base_amount) or 0.0,
                'tax_id_secondary': inv_t.tax_id.id or False,
                'partner_id': inv_t.tax_partner_id.id or False
            })
        return res


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def button_reset_taxes(self):
        account_invoice_tax_obj = self.env['account.invoice.tax']
        ctx = dict(self._context)
        res = super(AccountInvoice, self).button_reset_taxes()
        for invoice in self:
            partner = invoice.partner_id
            if not partner.is_broker_ok:
                continue
            else:
                self._cr.execute(
                    "DELETE FROM account_invoice_tax "
                    "WHERE invoice_id=%s AND manual is False", (invoice.id,))
                self.invalidate_cache()
                partner = invoice.partner_id
                if partner.lang:
                    ctx['lang'] = partner.lang
                for taxe in account_invoice_tax_obj.compute_broker(
                        invoice.with_context(ctx)).values():
                    for ltaxe in taxe:
                        account_invoice_tax_obj.create(taxe.get(ltaxe))
        # dummy write on self to trigger recomputations
        return res

    @api.multi
    def invoice_validate(self):
        """Inherit function to add raise if the partner is broker_ok and the
        product line not is type service, because is not is service can be
        real time and this try create a journal entry and this generates an
        error, by try made a division by zero
        """
        for inv in self:
            if inv.partner_id.is_broker_ok:
                for line in inv.invoice_line:
                    if not line.quantity and line.product_id.type != 'service':
                        raise except_orm(_('Error!'), _(
                            'You can´t add a line with quantity = 0 if the '
                            'product not is service, the product must be type '
                            'service.'))
        return super(AccountInvoice, self).invoice_validate()

    @api.model
    def line_get_convert(self, line, part, date):
        """Super to write in the line of move the partner from tax
        """
        res = super(AccountInvoice, self).line_get_convert(
            line, part, date)
        res = dict(res, partner_id=line.get('partner_id', False) or part)
        return res

    @api.multi
    def check_tax_lines(self, compute_taxes):
        account_invoice_tax_var = self.env['account.invoice.tax']
        if not self.partner_id.is_broker_ok:
            super(AccountInvoice, self).check_tax_lines(compute_taxes)
        else:
            for tax in compute_taxes.values():
                invoice_id = tax.get('invoice_id', False)
                break
            if invoice_id:
                compute_taxes = account_invoice_tax_var.compute_broker(
                    self.browse(invoice_id))
            company_currency = self.company_id.currency_id
            if not self.tax_line:
                for tax in compute_taxes.values():
                    for ltaxe in tax:
                        account_invoice_tax_var.create(tax.get(ltaxe))
            else:
                tax_key = []
                for tax in self.tax_line:
                    if tax.manual:
                        continue
                    # start custom change
                    key = (tax.tax_id.id)
                    # end custom change
                    tax_key.append(key)
                    if key not in compute_taxes:
                        raise except_orm(
                            _('Warning!'), _(
                                'Global taxes defined, but they are not in '
                                'invoice lines !'))
                    base = 0.0
                    for ctax in compute_taxes.get(key).values():
                        if ctax.get('tax_partner_id', False) ==\
                                tax.tax_partner_id.id:
                            base = ctax.get('base', 0.0)
                            if abs(base - tax.base) >\
                                    company_currency.rounding:
                                raise except_orm(
                                    _('Warning!'),
                                    _('Tax base different!\nClick on compute '
                                        'to update the tax base.'))
                for key in compute_taxes:
                    if key not in tax_key:
                        raise except_orm(_('Warning!'), _(
                            'Taxes are missing!\nClick on compute button.'))
