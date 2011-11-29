# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://moylop.blogspot.com/
#    All Rights Reserved.
#    info moylop260 (moylop260@hotmail.com)
############################################################################
#    Coded by: moylop260 (moylop260@hotmail.com)
#    Launchpad Project Manager for Publication: Nhomar Hernandez - nhomar@openerp.com.ve
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

from osv import osv
from osv import fields
import tools
from tools.translate import _
import netsvc
import time
import os

class account_invoice_tax(osv.osv):
    _inherit= "account.invoice.tax"
    
    def _get_tax_data(self, cr, uid, ids, field_names=None, arg=False, context={}):
        if not context:
            context = {}
        res = {}
        for invoice_tax in self.browse(cr, uid, ids, context=context):
            res[invoice_tax.id] = {}
            tax_name = invoice_tax.name.lower().replace('.','').replace(' ', '').replace('-', '')
            tax_percent = invoice_tax.amount and invoice_tax.base and invoice_tax.amount*100.0 / abs( invoice_tax.base ) or 0.0
            if 'iva' in tax_name:
                tax_name = 'IVA'
                tax_percent = round(tax_percent, 0)#Hay problemas de decimales al calcular el iva, y hasta ahora el iva no tiene decimales
            elif 'isr' in tax_name:
                tax_name = 'ISR'
            elif 'ieps' in tax_name:
                tax_name = 'IEPS'
            res[invoice_tax.id]['name2'] = tax_name
            res[invoice_tax.id]['tax_percent'] = tax_percent
            #res[invoice_tax.id]['amount'] = invoice_tax.amount
        return res
    
    _columns = {
        'name2': fields.function(_get_tax_data, method=True, type='char', size=32, string='Name2', multi='tax_percent', store=True),
        'tax_percent': fields.function(_get_tax_data, method=True, type='float', string='Tax Percent', multi='tax_percent', store=True),
    }
account_invoice_tax()
