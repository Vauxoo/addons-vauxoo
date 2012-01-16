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
#from tools import amount_to_text
import tools
import time
from xml.dom import minidom
import os
import base64
#import libxml2
#import libxslt
#import zipfile
#import StringIO
#import OpenSSL
import hashlib
import tempfile
import os
import netsvc
from tools.translate import _
import codecs
import release
from datetime import datetime

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def _get_facturae_invoice_dict_data(self, cr, uid, ids, context={}):
        invoice_data_parents = super(account_invoice,self)._get_facturae_invoice_dict_data(cr,uid,ids,context)

        date_invoice = datetime.strptime( invoice_data_parents[0]['date_invoice'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        if date_invoice < '2012-01-01':
          #  print 'es menor'
            return invoice_data_parents
        else:
            invoice = self.browse(cr, uid, context['active_id'], context={'date':date_invoice})
            rate_obj = self.pool.get('res.currency')
            invoice_data_parents[0]['Comprobante']['xsi:schemaLocation'] = 'http://www.sat.gob.mx/cfd/2 http://www.sat.gob.mx/sitio_internet/cfd/2/cfdv22.xsd'
            invoice_data_parents[0]['Comprobante']['version'] = '2.2'
            
            invoice_data_parents[0]['Comprobante']['TipoCambio'] = invoice.currency_id.rate or 1
            invoice_data_parents[0]['Comprobante']['Moneda'] = invoice.currency_id.name or ''
            #~ invoice_data_parents[0]['Comprobante']['metodoDePago'] = pendiente metodo de pago
            #~ invoice_data_parents[0]['Comprobante']['LugarExpedicion'] = pendiente 
            #~ invoice_data_parents[0]['Comprobante']['NumCtaPago'] = pendiente 
            invoice_data_parents[0]['Comprobante']['metodoDePago'] = invoice.pay_method_id.name or ''
            invoice_data_parents[0]['Comprobante']['Emisor']['RegimenFiscal'] = invoice.partner_id.regimen_fiscal_id.name or ''
            print '-----------el regimen es',invoice.partner_id.regimen_fiscal_id.name 
        
        return invoice_data_parents
    _columns = {
        'pay_method_id': fields.many2one('pay.method', 'Metodo de Pago', required = True, readonly=True, states={'draft':[('readonly',False)]}),
        
    }
account_invoice()
