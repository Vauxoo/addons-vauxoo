# -*- encoding: utf-8 -*-
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


class account_invoice_tax(models.Model):
    _inherit = 'account.invoice.tax'

    tax_partner_id = fields.Many2one('res.partner', 'Supplier', readonly=True)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    invoice_broker_id = fields.Many2one(
        'account.invoice', 'Invoice Broker', help='If this invoice line is to '
        'the payment to a broker, indicate the original invoice that must be '
        'generated the broker partner', domain=[('type', '=', 'in_invoice')])
    partner_broker_ok = fields.Boolean(
        string='Partner Broker', related='invoice_id.partner_id.is_broker_ok',
        store=False, help='Indicate if the partner to invoice is broker')


class account_invoice_tax(models.Model):
    _inherit = "account.invoice.tax"

    @api.v8
    def compute(self, invoice):
        """
        Super to this method, to calculate values to taxes from lines that your
        quantity is 0, and have invoice_broker_id.
        """
        currency = invoice.currency_id.with_context(
            date=invoice.date_invoice or
            fields.Date.context_today(invoice))
        company_currency = invoice.company_id.currency_id
        res = super(account_invoice_tax, self).compute(invoice)
        for line in invoice.invoice_line:
            if line.invoice_broker_id and line.quantity == 0:
                taxes = line.invoice_line_tax_id.compute_all(
                    (line.price_unit * (1 - (line.discount or 0.0) / 100.0)),
                    1.0, line.product_id, invoice.partner_id)['taxes']
                for tax in taxes:
                    if res.get(tax.get('id', False), False):
                        am_base = res.get(tax.get('id')).get('base', 0.0)
                        tot_am_base = am_base + currency.round(
                            tax.get('price_unit', 0.0))
                        base_amount = res.get(tax.get('id')).get(
                            'base_amount', 0.0) + currency.compute(
                            tot_am_base * tax.get('base_sign', 0.0),
                            company_currency, round=False)
                        res.get(tax.get('id')).update({
                            'base': tot_am_base,
                            'tax_partner_id':
                                line.invoice_broker_id.partner_id and
                                line.invoice_broker_id.partner_id.id or
                                False,
                            'amount': tax.get('amount', 0.0),
                            'base_amount': base_amount,
                            'tax_amount': currency.compute(
                                tax.get('amount', 0.0) *
                                tax.get('tax_sign', 0.0), company_currency,
                                round=False)})
        return res

    def move_line_get(self, cr, uid, invoice_id, context=None):
        '''
        Super to function, to add partner_id in dict, this to create the
        line corresponding to tax with the partner to this, this when the
        line of tax is to register cost of to broker
        '''
        res = super(account_invoice_tax, self).move_line_get(
            cr, uid, invoice_id, context=context)
        tax_invoice_ids = self.search(cr, uid, [
            ('invoice_id', '=', invoice_id)], context=context)
        for inv_t in self.browse(cr, uid, tax_invoice_ids, context=context):
            tax_name = inv_t.name or ''
            tax_acc_id = inv_t.account_id.id
            tax_code_id = inv_t.tax_code_id.id or None
            if inv_t.tax_partner_id:
                for tax in res:
                    if tax.get('name', '') == tax_name and tax.get(
                            'account_id', False) == tax_acc_id and tax.get(
                            'tax_code_id', False) == tax_code_id:
                        tax.update({
                            'partner_id': inv_t.tax_partner_id.id or False})
        return res


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        '''
        Inherit function to add raise if the partner is broker_ok and the
        product line not is type service, because is not is service can be
        real time and this try create a journal entry and this generates an
        error, by try made a division by zero
        '''
        for inv in self:
            if inv.partner_id.is_broker_ok:
                for line in inv.invoice_line:
                    if not line.quantity and line.product_id.type != 'service':
                        raise except_orm(_('Error!'), _(
                            'You can´t add a line with quantity = 0 if the '
                            'product not is service, the product must be type '
                            'service.'))
        return super(account_invoice, self).invoice_validate()

    @api.model
    def line_get_convert(self, line, part, date):
        '''
        Super to write in the line of move the partner from tax
        '''
        res = super(account_invoice, self).line_get_convert(
            line, part, date)
        res = dict(res, partner_id=line.get('partner_id', False) or part)
        return res
