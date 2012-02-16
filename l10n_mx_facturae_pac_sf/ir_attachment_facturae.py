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
import wizard
import netsvc
import pooler
import time
import base64
import StringIO
import csv
import tempfile
import os
import sys
import codecs
import xml.dom.minidom
import l10n_mx_facturae_pac_sf
from datetime import datetime
from tools.misc import ustr
try:
    from SOAPpy import WSDL
except:
    print "Package SOAPpy missed"
    pass
import time


class ir_attachment_facturae_mx(osv.osv):
    _inherit = 'ir.attachment.facturae.mx'

    def _get_type(self, cr, uid, ids=None, context=None):
        types = super(ir_attachment_facturae_mx, self)._get_type(cr, uid, ids, context=context)
        types.append( ('cfdi2011_pac_solfact', 'CFDI 2011 PAC Solucion Factible') )
        return types
    
    _columns = {
        'type': fields.selection(_get_type, 'Type', type='char', size=64),
    }
        
    def sign_pac_solfact(self, cr, uid, ids, context=None):
        invoice_id = self.browse(cr, uid, ids)[0].invoice_id.id
        pool = pooler.get_pool(cr.dbname)
        invoice_obj = pool.get('account.invoice')
        pac_params_obj = pool.get('params.pac')
        
        data = l10n_mx_facturae_pac_sf.wizard.wizard_export_invoice_pac_sf._get_file(self,cr, uid, {'ids':[invoice_id]}, context=context)
        data_dict_form = {}
        data_dict_form['form'] = data
        data_dict_form['ids'] = [invoice_id]
        #~ print 'el data_dict_form es',data_dict_form
        mensaje = l10n_mx_facturae_pac_sf.wizard.wizard_export_invoice_pac_sf._upload_ws_file(self,cr, uid, data_dict_form, context={'wkf':1})
        #~ res= {'value':{},'warning': {'title': ('Warning'), 'message': ('timbrado de Facturacion electronica')}}
        return mensaje
        
    def action_sign(self, cr, uid, ids, context=None):
        for attachment in self.browse(cr, uid, ids, context=context):
            if attachment.type == 'cfdi2011_pac_solfact':
                result = self.sign_pac_solfact(cr, uid, [attachment.id], context=context)
                file_xml = result['file']
                self.write(cr, uid, ids, {'file_xml_sign': file_xml})
        res = super(ir_attachment_facturae_mx, self).action_sign(cr, uid, ids, context=context)
        return res
    
    def action_printable(self, cr, uid, ids, context=None):
        for attachment in self.browse(cr, uid, ids, context=context):
            if attachment.type == 'cfdi2011_pac_solfact':#TODO: Aqui deberia de ir un reporte generico, para todos.
                report_name = 'account.invoice.facturae.pac.sf.pdf'
                service = netsvc.LocalService("report."+report_name)
                (result,format) = service.create(cr, uid, [attachment.invoice_id.id], {}, {})
                file_pdf = base64.encodestring( result )
                self.write(cr, uid, ids, {'file_pdf': file_pdf})
        res = super(ir_attachment_facturae_mx, self).action_printable(cr, uid, ids, context=context)
        return res

    def action_send_email(self, cr, uid, ids, context=None):
        return super(ir_attachment_facturae_mx, self).action_send_email(cr, uid, ids, context=context)
    
    def action_done(self, cr, uid, ids, context=None):
        return super(ir_attachment_facturae_mx, self).action_done(cr, uid, ids, context=context)
    
    def action_cancel(self, cr, uid, ids, context=None):
        return super(ir_attachment_facturae_mx, self).action_cancel(cr, uid, ids, context=context)
ir_attachment_facturae_mx()
