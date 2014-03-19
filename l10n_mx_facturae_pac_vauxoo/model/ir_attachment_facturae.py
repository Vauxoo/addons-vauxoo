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
try:
    from SOAPpy import WSDL
except:
    print "Package SOAPpy missed"#TODO: Warning message
    pass

class ir_attachment_facturae_mx(osv.Model):
    _inherit = 'ir.attachment.facturae.mx'

    def _get_type(self, cr, uid, ids=None, context=None):
        if context is None:
            context = {}
        types = super(ir_attachment_facturae_mx, self)._get_type(
            cr, uid, ids, context=context)
        types.extend([
            ('cfdi32_pac_vx', 'CFDI 3.2 Vauxoo'),
        ])
        return types

    def get_driver_fc_sign(self):
        factura_mx_type__fc = super(ir_attachment_facturae_mx, self).get_driver_fc_sign()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi32_pac_vx': self._upload_ws_file_vx})
        return factura_mx_type__fc

    def get_driver_fc_cancel(self):
        factura_mx_type__fc = super(ir_attachment_facturae_mx, self).get_driver_fc_cancel()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi32_pac_vx': self.sf_cancel})
        return factura_mx_type__fc

    _columns = {
        'type': fields.selection(_get_type, 'Type', type='char', size=64,
                                 required=True, readonly=True, help="Type of Electronic Invoice"),
    }

    def sf_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        msg = ''
        pac_params_obj = self.pool.get('params.pac')
        return True

    def _upload_ws_file_vx(self, cr, uid, ids, fdata=None, context=None):
        if context is None:
            context = {}
        HOST = config['xmlrpc_interface'] or '0.0.0.0'
        PORT = config['xmlrpc_port']
        DB = config['db_name']
        user = self.pool.get('res.users').browse(cr, uid, uid)
        USER = user.login
        PASS = user.password
        url ='http://%s:%d/xmlrpc/' % (HOST,PORT)
        common_proxy = xmlrpclib.ServerProxy(url+'common')
        object_proxy = xmlrpclib.ServerProxy(url+'object')
        uid = common_proxy.login(DB,USER,PASS)
        for attachment in self.browse(cr, uid, ids, context=context): 
            attachment_values = {
                                'name': attachment.file_input.name,
                                'datas': attachment.file_input.datas,
                                'datas_fname': attachment.file_input.datas_fname,
                                'res_model': attachment.file_input.res_model,
                                'res_id': False,
                                }
            attachment_id = object_proxy.execute(DB, uid, PASS, 'ir.attachment', 'create', attachment_values)
            attachment_face = { 'name': attachment.name, 
                                'type': 'cfdi32_pac_sf',
                                'company_id': attachment.company_id.id,
                                'journal_id': 11,
                                'id_source': False,
                                'model_source': attachment.model_source,
                                'attachment_email': '',
                                'certificate_password': '12345678a',
                                'certificate_file': '''MIIEdDCCA1ygAwIBAgIUMjAwMDEwMDAwMDAxMDAwMDU4NjcwDQYJKoZIhvcNAQEFBQAwggFvMRgw
            FgYDVQQDDA9BLkMuIGRlIHBydWViYXMxLzAtBgNVBAoMJlNlcnZpY2lvIGRlIEFkbWluaXN0cmFj
            acOzbiBUcmlidXRhcmlhMTgwNgYDVQQLDC9BZG1pbmlzdHJhY2nDs24gZGUgU2VndXJpZGFkIGRl
            IGxhIEluZm9ybWFjacOzbjEpMCcGCSqGSIb3DQEJARYaYXNpc25ldEBwcnVlYmFzLnNhdC5nb2Iu
            bXgxJjAkBgNVBAkMHUF2LiBIaWRhbGdvIDc3LCBDb2wuIEd1ZXJyZXJvMQ4wDAYDVQQRDAUwNjMw
            MDELMAkGA1UEBhMCTVgxGTAXBgNVBAgMEERpc3RyaXRvIEZlZGVyYWwxEjAQBgNVBAcMCUNveW9h
            Y8OhbjEVMBMGA1UELRMMU0FUOTcwNzAxTk4zMTIwMAYJKoZIhvcNAQkCDCNSZXNwb25zYWJsZTog
            SMOpY3RvciBPcm5lbGFzIEFyY2lnYTAeFw0xMjA3MjcxNzAyMDBaFw0xNjA3MjcxNzAyMDBaMIHb
            MSkwJwYDVQQDEyBBQ0NFTSBTRVJWSUNJT1MgRU1QUkVTQVJJQUxFUyBTQzEpMCcGA1UEKRMgQUND
            RU0gU0VSVklDSU9TIEVNUFJFU0FSSUFMRVMgU0MxKTAnBgNVBAoTIEFDQ0VNIFNFUlZJQ0lPUyBF
            TVBSRVNBUklBTEVTIFNDMSUwIwYDVQQtExxBQUEwMTAxMDFBQUEgLyBIRUdUNzYxMDAzNFMyMR4w
            HAYDVQQFExUgLyBIRUdUNzYxMDAzTURGUk5OMDkxETAPBgNVBAsTCFVuaWRhZCAxMIGfMA0GCSqG
            SIb3DQEBAQUAA4GNADCBiQKBgQC2TTQSPONBOVxpXv9wLYo8jezBrb34i/tLx8jGdtyy27BcesOa
            v2c1NS/Gdv10u9SkWtwdy34uRAVe7H0a3VMRLHAkvp2qMCHaZc4T8k47Jtb9wrOEh/XFS8LgT4y5
            OQYo6civfXXdlvxWU/gdM/e6I2lg6FGorP8H4GPAJ/qCNwIDAQABox0wGzAMBgNVHRMBAf8EAjAA
            MAsGA1UdDwQEAwIGwDANBgkqhkiG9w0BAQUFAAOCAQEATxMecTpMbdhSHo6KVUg4QVF4Op2IBhiM
            aOrtrXBdJgzGotUFcJgdBCMjtTZXSlq1S4DG1jr8p4NzQlzxsdTxaB8nSKJ4KEMgIT7E62xRUj15
            jI49qFz7f2uMttZLNThipunsN/NF1XtvESMTDwQFvas/Ugig6qwEfSZc0MDxMpKLEkEePmQwtZD+
            zXFSMVa6hmOu4M+FzGiRXbj4YJXn9Myjd8xbL/c+9UIcrYoZskxDvMxc6/6M3rNNDY3OFhBK+V/s
            PMzWWGt8S1yjmtPfXgFs1t65AZ2hcTwTAuHrKwDatJ1ZPfa482ZBROAAX1waz7WwXp0gso7sDCm2
            /yUVww==''',
                                'certificate_key_file': '''MIICxjBABgkqhkiG9w0BBQ0wMzAbBgkqhkiG9w0BBQwwDgQIV+FZR/7E9+8CAggAMBQGCCqGSIb3
            DQMHBAgiwhoDhotSegSCAoDi82IsNHCEL07pbLApGWi9yUN2uLoVxemj3ehNeYTBRa3i/1wPjmoE
            JG07sZSUG+bANexY82lL0zlNePXx58Pw2ZrnNgt4I1K3t1mk/cz3clz1sp6Xlwf2UQWPB0CIIxbu
            YLxWNnPJIYC0n7ovcsgqrP7W0t0Tk/oDPFWxYAFKHI7b+Sbeg/r7IYJWQb6esY7KDjSeFZ+1qAse
            vVv9+db6c5h1qiUNkqe9LoSCyF1T6pSmKPdChmA/AV5gP7VKN5Sjactd3dMT85JDxFR6vgkAclKy
            SJc0FGgeu1G8BdzX2sDjtoy00Q+ImZYzdDnuZbBJKVDnR42ox/Wgzv9FyqwKACF+tRxAifDxjWTh
            McUFlZCLZFX/Mr56royDHVH5TImJ5eqy2KYuoYcIXPREmV/XGXjGWhOED8HX/8nNlF0Zt7GWzARj
            U4hBzt8ONIbmVzV7G+42zQ1jGi3sZgLSW2BmbZvLkePsSO0cLtE2UEFhq54i8kN1V8j/GJI24ob6
            PhxuT8SGxZHi4fWBT8w3irgAdrIgQzm5Re53bA+/QAzlNUXvmW3cHE8iWvDbyiLiUGvBRPjNJYoL
            fgHRkhfZ4l++fucP8V0kuau/+w/R6skQjNEbBPlqo6bqcme/ErzVOf4mYE9cfL7xZ14A30Ri13uR
            rCrR5PJJirXZ9EP0EsCMKRPUQ6bT3jPgLUBd965ADYZmOR6tGxRQgC4X2iXg99N08+/H6Et2Ox4C
            qKB637nTnBgTrWrrOxGhivYSr2sogItw35uqu5IM6scuvNmzes8Wv0lYn/R3rSv7cvOWTxqFfT0T
            w5Y+c5ypauUSDyY6TQVB9qPf3Wwl0QP20sEY4exP''',
                                'user_pac': 'testing@solucionfactible.com',
                                'password_pac': 'timbrado.SF.16672',
                                'url_webservice_pac': 'http://testing.solucionfactible.com/ws/services/Timbrado',
                                'file_input': attachment.file_input.id,
                                'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                               }
            attachment_face_id = object_proxy.execute(DB, uid, PASS, 'ir.attachment.facturae.mx', 'create', attachment_face)
            object_proxy.execute(DB, uid, PASS,'ir.attachment.facturae.mx','signal_confirm',[attachment_face_id])
            try:
                object_proxy.execute(DB, uid, PASS,'ir.attachment.facturae.mx','signal_sign',[attachment_face_id])
            except Exception, e:
                raise osv.except_osv(_("failed!"), _("FacturaE:\n %s") % tools.ustr(e))                
            ir_attach = object_proxy.execute(DB, uid, PASS,'ir.attachment.facturae.mx','read',[attachment_face_id],['file_xml_sign'])
            data = object_proxy.execute(DB, uid, PASS,'ir.attachment','read',[ir_attach[0]['file_xml_sign'][0]],['db_datas'])
            xml_sign = base64.decodestring(data[0]['db_datas']) or ''
            file = base64.encodestring(xml_sign or '')
        return {'file': file, 'msg': 'QUE EXITO!', 'cfdi_xml': xml_sign, 'status': True}
           
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
