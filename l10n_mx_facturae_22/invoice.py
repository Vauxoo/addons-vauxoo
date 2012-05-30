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
        if date_invoice < '2012-07-01':
          #  print 'es menor'
            return invoice_data_parents
        else:
            invoice = self.browse(cr, uid, ids, context={'date':date_invoice})[0]
            city = invoice_data_parents[0]['Comprobante']['Emisor']['DomicilioFiscal']['municipio']
            state = invoice_data_parents[0]['Comprobante']['Emisor']['DomicilioFiscal']['estado']
            country = invoice_data_parents[0]['Comprobante']['Emisor']['DomicilioFiscal']['pais']
            if city and state and country:
                address = city +' '+ state +', '+ country
            else:
                raise osv.except_osv(('Domicilio Incompleto!'),('Verifique que el domicilio de la compañia emisora del comprobante fiscal este completo (Ciudad - Estado - Pais)'))
            
            if not invoice.company_id.partner_id.regimen_fiscal_id.name:
                raise osv.except_osv(('Regimen Fiscal Faltante!'),('El Regimen Fiscal de la compañia emisora del comprobante fiscal es un dato requerido'))
                
            invoice_data_parents[0]['Comprobante']['xsi:schemaLocation'] = 'http://www.sat.gob.mx/cfd/2 http://www.sat.gob.mx/sitio_internet/cfd/2/cfdv22.xsd'
            invoice_data_parents[0]['Comprobante']['version'] = '2.2'
            invoice_data_parents[0]['Comprobante']['TipoCambio'] = invoice.rate or 1
            invoice_data_parents[0]['Comprobante']['Moneda'] = invoice.currency_id.name or ''
            invoice_data_parents[0]['Comprobante']['NumCtaPago'] = invoice.acc_payment.acc_number or 'No identificado'
            invoice_data_parents[0]['Comprobante']['metodoDePago'] = invoice.pay_method_id.name or 'No identificado'
            invoice_data_parents[0]['Comprobante']['Emisor']['RegimenFiscal'] = {'Regimen':invoice.company_id.partner_id.regimen_fiscal_id.name or ''}
            invoice_data_parents[0]['Comprobante']['LugarExpedicion'] = address
        
        return invoice_data_parents
    
    def onchange_partner_id(self, cr, uid, ids, type, partner_id, date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False, currency_id=False):
        res = super(account_invoice,self).onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice, payment_term, partner_bank_id, company_id, currency_id)
        partner_bank_obj = self.pool.get('res.partner.bank')
        acc_partner_bank = False
        if partner_id:
            acc_partner_bank_ids = partner_bank_obj.search(cr, uid,[('partner_id', '=', partner_id), ('currency_id', '=', currency_id)], limit = 1)
            if not acc_partner_bank_ids:
                acc_partner_bank_ids = partner_bank_obj.search(cr, uid,[('partner_id', '=', partner_id), ('currency_id', '=', False)], limit = 1)
            acc_partner_bank = acc_partner_bank_ids and partner_bank_obj.browse(cr, uid, acc_partner_bank_ids)[0] or False
        res['value']['acc_payment'] = acc_partner_bank and acc_partner_bank.id or False
        return res
    
    def _get_file_globals(self, cr, uid, ids, context={}):
        
        file_global= super(account_invoice, self)._get_file_globals(cr, uid, ids)
        date_invoice = self.browse(cr, uid,ids)[0].date_invoice
        if date_invoice >= '2012-07-01 00:00:00':
            file_global['fname_xslt'] = os.path.join( tools.config["addons_path"], 'l10n_mx_facturae', 'SAT', 'cadenaoriginal_2_2.xslt' ) #para cfd 2.2
        return file_global
        
    _columns = {
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft':[('readonly',False)]}, change_default=True),
        'pay_method_id': fields.many2one('pay.method', 'Metodo de Pago', readonly=True, states={'draft':[('readonly',False)]}, help = 'Indica la forma en que se pagó o se pagará la factura, donde las opciones pueden ser: cheque, transferencia bancaria, depósito en cuenta bancaria, tarjeta de crédito, efectivo etc. Si no se sabe como va ser pagada la factura, dejarlo vacío y en el xml aparecerá “No identificado”.'),
        'acc_payment': fields.many2one ('res.partner.bank', 'Numero de cuenta', readonly=True, states={'draft':[('readonly',False)]},help = 'Es la cuenta con la que el cliente pagará la factura, si no se sabe con cual cuenta se va pagar dejarlo vacío y en el xml aparecerá "No identificado".'),
    }
account_invoice()
