# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Launchpad Project Manager for Publication: Nhomar Hernandez - nhomar@vauxoo.com
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools
from openerp import netsvc

import time
import os


class account_invoice_tax(osv.Model):
    _inherit = "account.invoice.tax"

    def _get_tax_data(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if context is None:
            context = {}
        res = {}
        for invoice_tax in self.browse(cr, uid, ids, context=context):
            res[invoice_tax.id] = {}
            tax = 'tax_id' in self._columns and invoice_tax.tax_id or False  # If patch apply and module account_invoice_tax install
            tax_name = (tax and tax.tax_category_id and \
                tax.tax_category_id.code or invoice_tax.name).upper().replace(
                '.', '').replace(' ', '').replace('-', '')
            tax_percent = (
                tax and tax.amount*100.0 or False)  # validate? type='percent'
            tax_percent = tax_percent or (
                invoice_tax.amount and invoice_tax.base and \
                invoice_tax.amount*100.0 / abs(invoice_tax.base) or 0.0)
            if 'IVA' in tax_name:
                tax_name = 'IVA'
                if not tax and tax_percent > 0:
                    tax_percent = round(
                        tax_percent, 0)  # Hay problemas de decimales al calcular el iva, y hasta ahora el iva no tiene decimales
            elif 'ISR' in tax_name:
                tax_name = 'ISR'
            elif 'IEPS' in tax_name:
                tax_name = 'IEPS'
            res[invoice_tax.id]['name2'] = tax_name
            res[invoice_tax.id]['tax_percent'] = tax_percent
            # res[invoice_tax.id]['amount'] = invoice_tax.amount
        return res

    _columns = {
        'name2': fields.function(_get_tax_data, method=True, type='char',
                size=64, string='Tax Short Name', multi='tax_percent',
                store=True, help="Is the code of category of the tax or name \
                of tax but in uppers, without '.', '-', ' '"),
        'tax_percent': fields.function(_get_tax_data, method=True, type='float',
                string='Tax Percent', multi='tax_percent', store=True,),
    }
