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

    tax_partner_id = fields.Many2one('res.partner', 'Partner')


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    invoice_broker_id = fields.Many2one(
        'account.invoice', 'Invoice Broker', help='If this invoice line is to '
        'the payment to a broker, indicate the original invoice that must be'
        'generated the broker partner', domain=[('type', '=', 'in_invoice')])
    partner_broker_ok = fields.Boolean(
        'Partner Broker', compute='_get_partner_broker_ok',
        help='Indicate if the partner to invoice is broker')

    @api.model
    def move_line_get_item(self, line):
        res = super(AccountInvoiceLine, self).move_line_get_item(line)
        res = dict(
            res, partner_id=line.invoice_broker_id.partner_id.id or None)
        return res

    @api.one
    @api.depends('invoice_id.partner_id')
    def _get_partner_broker_ok(self):
        self.partner_broker_ok = self.invoice_id and\
            self.invoice_id.partner_id and\
            self.invoice_id.partner_id.is_broker_ok


    class account_invoice_tax(models.Model):
        _inherit = "account.invoice.tax"
    
        @api.v8
        def compute(self, invoice):
            currency = invoice.currency_id.with_context(
                date=invoice.date_invoice or fields.Date.context_today(invoice))
            res = super(account_invoice_tax, self).compute(invoice)
            for line in invoice.invoice_line:
                if line.invoice_broker_id:
                    taxes = line.invoice_line_tax_id.compute_all(
                        (line.price_unit * (1 - (line.discount or 0.0) / 100.0)),
                        1.0, line.product_id, invoice.partner_id)['taxes']
                    for tax in taxes:
                        if res.get(tax.get('id', False), False):
                            am_base = res.get(tax.get('id')).get('base', 0.0)
                            res.get(tax.get('id')).update({
                                'base': am_base + currency.round(
                                    tax.get('price_unit', 0.0)),
                                'tax_partner_id': line.invoice_broker_id.\
                                    partner_id and line.invoice_broker_id.\
                                    partner_id.id or False,
                                'amount': tax.get('amount', 0.0)})
            return res
