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

from openerp import models, fields, api


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
        'Partner Broker', compute='_get_partner_broker_ok',
        help='Indicate if the partner to invoice is broker')

    @api.one
    @api.depends('invoice_id.partner_id')
    def _get_partner_broker_ok(self):
        '''
        If the partner to invoice is broker this field is True, is to only can
        load a invoice broker in lines to invoice with broker ok == True.
        '''
        self.partner_broker_ok = self.invoice_id and\
            self.invoice_id.partner_id and\
            self.invoice_id.partner_id.is_broker_ok


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
                        res.get(tax.get('id')).update({
                            'base': tot_am_base,
                            'tax_partner_id':
                                line.invoice_broker_id.partner_id and
                                line.invoice_broker_id.partner_id.id or
                                False,
                            'amount': tax.get('amount', 0.0),
                            'base_amount': currency.compute(
                                tot_am_base * tax.get('base_sign', 0.0),
                                company_currency, round=False),
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
            tax_acc = inv_t.account_id.id or False
            if inv_t.tax_partner_id:
                for tax in res:
                    if tax.get('name', '') == tax_name and tax.get(
                            'account_id', False) == tax_acc:
                        tax.update({
                            'partner_id': inv_t.tax_partner_id.id or False})
        return res


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def line_get_convert(self, line, part, date):
        '''
        Super to write in the line of move the partner from tax
        '''
        res = super(account_invoice, self).line_get_convert(
            line, part, date)
        res = dict(res, partner_id=line.get('partner_id', False) or part)
        return res
