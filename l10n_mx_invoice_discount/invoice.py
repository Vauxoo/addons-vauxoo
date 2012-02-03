# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Coded by: isaac (isaac@vauxoo.com)
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
import time
from xml.dom import minidom
import os
import base64
import hashlib
import tempfile
import os
import netsvc
from tools.translate import _
import codecs
import release
from datetime import datetime
import decimal_precision as dp

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def _get_facturae_invoice_dict_data(self, cr, uid, ids, context={}):
        invoice_data_parents = super(account_invoice,self)._get_facturae_invoice_dict_data(cr,uid,ids,context)
        invoice = self.browse(cr, uid, ids)[0]
        sub_tot=0
        for line in invoice.invoice_line:
            sub_tot+=line.price_unit * line.quantity
            invoice_data_parents[0]['Comprobante']['Conceptos'][invoice.invoice_line.index(line)]['Concepto']['cantidad']=  line.quantity or '0.0'
            invoice_data_parents[0]['Comprobante']['Conceptos'][invoice.invoice_line.index(line)]['Concepto']['descripcion']= line.name or ' '
            invoice_data_parents[0]['Comprobante']['Conceptos'][invoice.invoice_line.index(line)]['Concepto']['importe']= line.price_unit * line.quantity or '0'
            invoice_data_parents[0]['Comprobante']['Conceptos'][invoice.invoice_line.index(line)]['Concepto']['noIdentificacion']= line.product_id.default_code or '-'
            invoice_data_parents[0]['Comprobante']['Conceptos'][invoice.invoice_line.index(line)]['Concepto']['unidad']= line.uos_id and line.uos_id.name or ''
            invoice_data_parents[0]['Comprobante']['Conceptos'][invoice.invoice_line.index(line)]['Concepto']['valorUnitario']= line.price_unit or '0'

        invoice_data_parents[0]['Comprobante']['motivoDescuento'] = invoice.partner_id.motive_discount or ''
        invoice_data_parents[0]['Comprobante']['descuento'] = invoice.global_discount or '0'
        invoice_data_parents[0]['Comprobante']['subTotal']=sub_tot
        
        return invoice_data_parents
    
    _columns = {
        'global_discount': fields.float('Global Discount'),
        'global_discount_percent': fields.float('Global Discount Percent'),
    }
account_invoice()

class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
    _columns = {
        'discount': fields.float('Discount (%)', digits_compute= dp.get_precision('Account'), readonly = True),
    }
account_invoice_line()
