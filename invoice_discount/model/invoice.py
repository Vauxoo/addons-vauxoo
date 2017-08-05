# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
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
"""File to add functionality in account.invoice.line to get the amount without
discount and the value of the discount
"""
from openerp import api, fields, models


class AccountInvoiceLine(models.Model):

    """Inherit from account.invoice.line to get by line the amount without
    discount and the amount of this
    """
    _inherit = 'account.invoice.line'

    subtotal_wo_discount = fields.Float(
        store=True, string="SubTotal w/o Discount",
        help=('Amount without apply the discount of the line, '
              'is calculated as Qty * Price Unit'),
        compute='_compute_subtotal_wo_disc')
    discount_amount = fields.Float(
        store=True, string='Discount Amount',
        help=('Amount total of the discount, is calculated as '
              'Discount * SubTotal w/o Discount / 100.'),
        compute='_compute_subtotal_wo_disc')

    @api.depends('invoice_line_tax_id', 'price_unit', 'quantity', 'discount')
    def _compute_subtotal_wo_disc(self):
        """Method to get the subtotal of the amount without discount
        """
        for line in self:
            taxes = line.invoice_line_tax_id.compute_all(
                line.price_unit, line.quantity)
            line.subtotal_wo_discount = taxes['total']
            line.discount_amount = (
                line.discount * line.subtotal_wo_discount / 100)


class AccountInvoice(models.Model):

    """Inherit from account.invoice to get the amount total without discount and
    the amount total of this, of all invoice lines.
    """
    _inherit = 'account.invoice'

    subtotal_wo_discount = fields.Float(
        compute='_compute_subtotal_wo_disc', string='SubTotal w/o Discount',
        store=True,
        help='Amount without apply the discount of the lines of the invoice.')
    discount_amount = fields.Float(
        compute='_compute_subtotal_wo_disc',  string='Discount', store=True,
        help='Total of discount apply in each line of the invoice.')

    @api.depends('invoice_line.subtotal_wo_discount',
                 'invoice_line.discount_amount')
    def _compute_subtotal_wo_disc(self):
        # TODO: Use read_group method here
        for invoice in self:
            invoice._cache['subtotal_wo_discount'] = 0
            invoice._cache['discount_amount'] = 0
            for line in invoice.invoice_line:
                invoice._cache['subtotal_wo_discount'] += (
                    line.subtotal_wo_discount)
                invoice._cache['discount_amount'] += line.discount_amount
