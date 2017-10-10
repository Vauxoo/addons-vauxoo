# coding: utf-8
# ##########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# ##########################################################################
#    Coded by: Luis Ernesto García Medina(ernesto_gm@vauxoo.com)
# ##############Credits#####################################################
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
# ##########################################################################
import re
from psycopg2 import IntegrityError

from openerp import api, fields, models, _
from openerp import exceptions


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    supplier_invoice_number_strip = fields.Char(
        compute='_compute_supplier_invoice_number_strip', store=True)

    @api.multi
    @api.depends('supplier_invoice_number', 'state', 'type')
    def _compute_supplier_invoice_number_strip(self):
        for invoice in self.filtered(
                lambda inv: inv.state not in ['draft', 'cancel'] and
                inv.type in ['in_invoice', 'in_refund'] and
                inv.supplier_invoice_number):
            invoice.supplier_invoice_number_strip = re.sub(
                r'\W+|\_', '', invoice.supplier_invoice_number.lower())

    @api.multi
    def invoice_validate(self):
        try:
            res = super(AccountInvoice, self).invoice_validate()
        except IntegrityError:
            raise exceptions.Warning(
                _('Error you can not validate the invoice with '
                  'supplier invoice number duplicated.'))
        return res

    _sql_constraints = [
        ('unique_supplier_invoice_number_strip', 'UNIQUE('
         'supplier_invoice_number_strip, company_id, commercial_partner_id)',
         'Error you can not validate the invoice with '
         'supplier invoice number duplicated.')]
