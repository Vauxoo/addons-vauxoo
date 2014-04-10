# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by:
#    Financed by:
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
        factura_mx_type__fc.update({'cfdi32_pac_vx': self._vauxoo_stamp})
        return factura_mx_type__fc

    def get_driver_fc_cancel(self):
        factura_mx_type__fc = super(ir_attachment_facturae_mx, self).get_driver_fc_cancel()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi32_pac_vx': self._vauxoo_cancel})
        return factura_mx_type__fc

    def _vauxoo_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
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
            DB = cr.dbname
            wsdl_url = pac_params.url_webservice or attachment.res_pac.url_webservice
            USER = pac_params.user or attachment.res_pac.user
            PASS = pac_params.password or attachment.res_pac.password
            url ='http://%s/xmlrpc/' % (wsdl_url)
            common_proxy = xmlrpclib.ServerProxy(url+'common')
            object_proxy = xmlrpclib.ServerProxy(url+'object')
            try:
                uid2 = common_proxy.login(DB,USER,PASS)
            except Exception, e:
                error = tools.ustr(traceback.format_exc())
                _logger.error(error)
            _args = [('cfdi_folio_fiscal', '=', attachment.cfdi_folio_fiscal),('res_pac','!=',attachment.res_pac.id)]
            ids_new = object_proxy.execute(DB, uid2, PASS, 'ir.attachment.facturae.mx', 'search', _args)
            try:
                res = object_proxy.execute(DB, uid2, PASS, 'ir.attachment.facturae.mx', 'signal_cancel', ids_new)
                msg = object_proxy.execute(DB, uid2, PASS,'ir.attachment.facturae.mx','read',ids_new,['msj'])[0]['msj']
                return {'message': msg, 'status': True}
            except Exception, e:
                error = tools.ustr(traceback.format_exc())
                _logger.error(error)

    def _vauxoo_stamp(self, cr, uid, ids, fdata=None, context=None):
        if context is None:
            context = {}
        pac_params_obj = self.pool.get('params.pac')
        for attachment in self.browse(cr, uid, ids, context=context):
            pac_params_ids = pac_params_obj.search(cr, uid, [
                ('method_type', '=', 'firmar'),
                ('res_pac', '=', attachment.res_pac.id),
                ('company_id', '=', attachment.company_id.id),
                ('active', '=', True)], limit=1, context=context)
            if pac_params_ids:
                pac_params = pac_params_obj.browse(
                    cr, uid, pac_params_ids, context)[0]
            DB = cr.dbname
            wsdl_url = pac_params.url_webservice or attachment.res_pac.url_webservice
            USER = pac_params.user or attachment.res_pac.user
            PASS = pac_params.password or attachment.res_pac.password
            url ='http://%s/xmlrpc/' % (wsdl_url)
            common_proxy = xmlrpclib.ServerProxy(url+'common')
            object_proxy = xmlrpclib.ServerProxy(url+'object')
            try:
                uid2 = common_proxy.login(DB,USER,PASS)
            except Exception, e:
                error = tools.ustr(traceback.format_exc())
                _logger.error(error)
            fname_cer_no_pem = self.binary2file(cr, uid, ids,
                    attachment.certificate_file, 'openerp_' + '' + '__certificate__', '.cer')
            cerCSD = fname_cer_no_pem and base64.encodestring(
                open(fname_cer_no_pem, "r").read()) or ''
            fname_key_no_pem = self.binary2file(cr, uid, ids,
                    attachment.certificate_key_file, 'openerp_' +'' + '__key__', '.key')
            keyCSD = fname_key_no_pem and base64.encodestring(
                open(fname_key_no_pem, "r").read()) or ''
            attachment_values = {
                                'name': attachment.file_input.name,
                                'datas': attachment.file_input.datas,
                                'datas_fname': attachment.file_input.datas_fname,
                                'res_model': attachment.file_input.res_model,
                                'res_id': False,
                                }
            attachment_id = object_proxy.execute(DB, uid2, PASS, 'ir.attachment', 'create', attachment_values)
            attachment_face = { 'name': attachment.name,
                                'company_id': attachment.company_id.id,
                                'id_source': False,
                                'model_source': attachment.model_source,
                                'attachment_email': '',
                                'certificate_password': attachment.certificate_password,
                                'certificate_file': cerCSD,
                                'certificate_key_file': keyCSD,
                                'user_pac': '',
                                'password_pac': '',
                                'url_webservice_pac': '',
                                'file_input': attachment.file_input.id,
                                'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'res_pac': 2, # This hardcore value must be changed
                               }
            attachment_face_id = object_proxy.execute(DB, uid2, PASS, 'ir.attachment.facturae.mx', 'create', attachment_face)
            object_proxy.execute(DB, uid2, PASS,'ir.attachment.facturae.mx','signal_confirm',[attachment_face_id])
            object_proxy.execute(DB, uid2, PASS,'ir.attachment.facturae.mx','signal_sign',[attachment_face_id])
            ir_attach = object_proxy.execute(DB, uid2, PASS,'ir.attachment.facturae.mx','read',[attachment_face_id],['file_xml_sign'])
            msg = object_proxy.execute(DB, uid2, PASS,'ir.attachment.facturae.mx','read',[attachment_face_id],['msj'])[0]['msj']
            ir_attach_ff = object_proxy.execute(DB, uid2, PASS,'ir.attachment.facturae.mx','read',[attachment_face_id],['cfdi_folio_fiscal'])
            cfdi_folio_fiscal = ir_attach_ff[0]['cfdi_folio_fiscal']
            if cfdi_folio_fiscal:
                self.write(cr, uid, attachment.id, {'cfdi_folio_fiscal': cfdi_folio_fiscal})
            data = object_proxy.execute(DB, uid2, PASS,'ir.attachment','read',[ir_attach[0]['file_xml_sign'][0]],['db_datas'])
            xml_sign = base64.decodestring(data[0]['db_datas']) or ''
            file = base64.encodestring(xml_sign or '')
        return {'file': file, 'msg': msg, 'cfdi_xml': xml_sign, 'status': True}
           
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
