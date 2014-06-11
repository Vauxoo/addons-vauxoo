# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Sabrina Romero <sabrina@vauxoo.com>  
#    Financed by: Vauxoo Consultores <info@vauxoo.com>
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

from openerp.tools.translate import _
from openerp.osv import fields, osv, orm
from openerp import tools
from openerp import netsvc
import openerp.tools.config as config
from openerp.tools.misc import ustr
import base64
import xml.dom.minidom
import time
import StringIO
import csv
import tempfile
import os
import sys
import codecs
from xml.dom import minidom
import urllib
import pooler
from openerp.tools.translate import _
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import time
import xmlrpclib
from openerp import tools
import logging
_logger = logging.getLogger(__name__)
import traceback
try:
    from SOAPpy import WSDL
except:
    print "Package SOAPpy missed"#TODO: Warning message
    pass

class ir_attachment_facturae_mx(osv.Model):
    _inherit = 'ir.attachment.facturae.mx'

    def get_driver_fc_sign(self):
        factura_mx_type__fc = super(ir_attachment_facturae_mx, self).get_driver_fc_sign()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi32_multipac_vx': self._vauxoo_stamp})
        return factura_mx_type__fc

    def get_driver_fc_cancel(self):
        factura_mx_type__fc = super(ir_attachment_facturae_mx, self).get_driver_fc_cancel()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi32_multipac_vx': self._vauxoo_cancel})
        return factura_mx_type__fc

    def _vauxoo_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        # Actually only cancel attachment of pac vauxoo in testing mode!
        if tools.config.options['test_enable']:
            wf_service = netsvc.LocalService("workflow")
            return {'message': {}, 'status': True}
            
        msg = ''
        pac_params_obj = self.pool.get('params.pac')
        for attachment in self.browse(cr, uid, ids, context=context):
            pac_params_ids = pac_params_obj.search(cr, uid, [
                ('method_type', '=', 'cancelar'),
                ('res_pac', '=', attachment.res_pac.id),
                ('company_id', '=', attachment.company_id.id),
                ('active', '=', True)], limit=1, context=context)
            if pac_params_ids:
                pac_params = pac_params_obj.browse(
                    cr, uid, pac_params_ids, context)[0]
                wsdl_url = pac_params.url_webservice or attachment.res_pac.url_webservice
                DB = wsdl_url[0:wsdl_url.find('.')]
                wsdl_url = wsdl_url[wsdl_url.find('.') + 1:]
                USER = pac_params.user or attachment.res_pac.user
                PASS = pac_params.password or attachment.res_pac.password
                url ='http://%s/xmlrpc/' % (wsdl_url)
                common_proxy = xmlrpclib.ServerProxy(url+'common')
                object_proxy = xmlrpclib.ServerProxy(url+'object')
                try:
                    uid2 = common_proxy.login(DB,USER,PASS)
                except:
                    raise osv.except_osv(_('Error !'),_('Could not establish the connection, please check parameters.'))
                fname_cer_no_pem = self.binary2file(cr, uid, ids,
                        attachment.certificate_file, 'openerp_' + '' + '__certificate__', '.cer')
                cerCSD = fname_cer_no_pem and base64.encodestring(
                        open(fname_cer_no_pem, "r").read()) or ''
                fname_key_no_pem = self.binary2file(cr, uid, ids,
                        attachment.certificate_key_file, 'openerp_' +'' + '__key__', '.key')
                keyCSD = fname_key_no_pem and base64.encodestring(
                        open(fname_key_no_pem, "r").read()) or ''
                params = [attachment.cfdi_folio_fiscal, attachment.certificate_password, cerCSD, keyCSD]
                res = object_proxy.execute(DB, uid2, PASS,'ir.attachment.facturae.client','cancel', [], *params)
                self.write(cr, uid, attachment.id, {'cfdi_fecha_cancelacion': res.pop('cfdi_fecha_cancelacion')})
                return res  

    def _vauxoo_stamp(self, cr, uid, ids, fdata=None, context=None):
        if context is None:
            context = {}
        ir_attach_client_obj = self.pool.get('ir.attachment.facturae.client')
        pac_params_obj = self.pool.get('params.pac')
        for attachment in self.browse(cr, uid, ids, context=context):
            
            # Actually not sing in testing mode!
            if tools.config.options['test_enable']:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, self._name, attachment.id, 'action_sign', cr)
                self.write(cr, uid, ids, {'file_xml_sign': attachment.file_input.id})
                return {'file': False, 'msg': {}, 'cfdi_xml': False, 'status': False}
                
            pac_params_ids = pac_params_obj.search(cr, uid, [
                ('method_type', '=', 'firmar'),
                ('res_pac', '=', attachment.res_pac.id),
                ('company_id', '=', attachment.company_id.id),
                ('active', '=', True)], limit=1, context=context)
            if pac_params_ids:
                pac_params = pac_params_obj.browse(
                    cr, uid, pac_params_ids, context)[0]
                wsdl_url = pac_params.url_webservice or attachment.res_pac.url_webservice
                DB = wsdl_url[0:wsdl_url.find('.')]
                wsdl_url = wsdl_url[wsdl_url.find('.') + 1:]
                USER = pac_params.user or attachment.res_pac.user
                PASS = pac_params.password or attachment.res_pac.password
                url ='http://%s/xmlrpc/' % (wsdl_url)
                common_proxy = xmlrpclib.ServerProxy(url+'common')
                object_proxy = xmlrpclib.ServerProxy(url+'object')
                try:
                    uid2 = common_proxy.login(DB,USER,PASS)
                except:
                    raise osv.except_osv(_('Error !'),_('Could not establish the connection, please check parameters.'))
                params = [base64.decodestring(attachment.file_input.datas), pac_params.user or attachment.res_pac.user, attachment.certificate_password]
                res = object_proxy.execute(DB, uid2, PASS,'ir.attachment.facturae.client','stamp', [], *params)
                self.write(cr, uid, attachment.id, {'cfdi_fecha_timbrado': res.pop('cfdi_fecha_timbrado'),
                                                        'cfdi_folio_fiscal': res.pop('cfdi_folio_fiscal'),
                                                        'cfdi_no_certificado': res.pop('cfdi_no_certificado'),
                                                        'cfdi_sello': res.pop('cfdi_sello'),
                                                        'cfdi_cadena_original': res.pop('cfdi_cadena_original')})
                return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
