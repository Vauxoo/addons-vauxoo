# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info moylop260 (moylop260@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Financed by: http://www.sfsoluciones.com (aef@sfsoluciones.com)
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
import base64

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    _columns = {
        'cfdi_cbb': fields.binary('CFD-I CBB'),
        'cfdi_sello': fields.text('CFD-I Sello'),
        'cfdi_no_certificado': fields.char('CFD-I Certificado', size=32),
        'cfdi_cadena_original': fields.text('CFD-I Cadena Original'),
        'cfdi_fecha_timbrado': fields.datetime('CFD-I Fecha Timbrado'),
        'cfdi_folio_fiscal': fields.char('CFD-I Folio Fiscal', size=64),
    }
    
    def cfdi_data_write(self, cr, uid, ids, cfdi_data, context={}):
        if not context:
            context = {}
        attachment_obj = self.pool.get('ir.attachment')
        cfdi_xml = cfdi_data.pop('cfdi_xml')
        if cfdi_xml:
            self.write(cr, uid, ids, cfdi_data)
            cfdi_data['cfdi_xml'] = cfdi_xml # Regresando valor, despues de hacer el write normal
            for invoice in self.browse(cr, uid, ids):
                #fname, xml_data = self.pool.get('account.invoice')._get_facturae_invoice_xml_data(cr, uid, [inv.id], context=context)
                fname_invoice = invoice.fname_invoice and invoice.fname_invoice + '.xml' or ''
                data_attach = {
                    'name': fname_invoice,
                    'datas': base64.encodestring( cfdi_xml or '') or False,
                    'datas_fname': fname_invoice,
                    'description': 'Factura-E XML CFD-I',
                    'res_model': 'account.invoice',
                    'res_id': invoice.id,
                }
                attachment_ids = attachment_obj.search(cr, uid, [('name','=',fname_invoice),('res_model','=','account.invoice'),('res_id', '=', invoice.id)])
                if attachment_ids:
                    attachment_obj.write(cr, uid, attachment_ids, data_attach, context=context)
                else:
                    attachment_obj.create(cr, uid, data_attach, context=context)
        return True
        
    def copy(self, cr, uid, id, default={}, context=None):
        if context is None:
            context = {}
        default.update({
            'cfdi_cbb': False,
            'cfdi_sello':False,
            'cfdi_no_certificado':False,
            'cfdi_cadena_original':False,
            'cfdi_fecha_timbrado': False,
            'cfdi_folio_fiscal': False,
        })
        return super(account_invoice, self).copy(cr, uid, id, default, context)
account_invoice()