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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools
from openerp import netsvc
from openerp import release
import time
import tempfile
import base64
import os
import traceback
import sys
from xml.dom import minidom
import xml.dom.minidom
from pytz import timezone
import pytz
import time
from datetime import datetime, timedelta

class ir_attachment_facturae_client(osv.Model):
    _name = 'ir.attachment.facturae.client'

    def stamp(self, cr, uid, ids, name, cfdi, user, password):
        ir_attch_obj = self.pool.get('ir.attachment')
        ir_attch_facte_obj = self.pool.get('ir.attachment.facturae.mx')
        ir_attachment_values = {'name': name + '.xml',
                                'datas': base64.encodestring(cfdi),
                                'datas_fname': name + '.xml',
                                'res_id': False,
                                }
        atta_id = ir_attch_obj.create(cr, uid, ir_attachment_values, context=None)
        ir_attachment_facte_values = { 'name': name,
                                        'id_source': False,
                                        'attachment_email': '',
                                        'certificate_password': password,
                                        'user_pac': '',
                                        'password_pac': '',
                                        'url_webservice_pac': '',
                                        'file_input': atta_id,
                                        'last_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                                        }
        atta_facte_id = ir_attch_facte_obj.create(cr, uid, ir_attachment_facte_values, context=None)
        ir_attch_facte_obj.signal_confirm(cr, uid, [atta_facte_id], context=None)
        ir_attch_facte_obj.signal_sign(cr, uid, [atta_facte_id], context=None)
        atta_facte_brw = ir_attch_facte_obj.browse(cr, uid, [atta_facte_id], context=None)
        format_xml = xml.dom.minidom.parseString(base64.decodestring(atta_facte_brw[0].file_xml_sign.datas)) or ''
        xml_sign = format_xml.toxml().encode('ascii', 'xmlcharrefreplace')
        arch = base64.encodestring(xml_sign) or ''
        res = {'file': arch, 
                'msg': atta_facte_brw[0].msj, 
                'cfdi_xml': xml_sign, 
                'status': True, 
                'cfdi_fecha_timbrado': atta_facte_brw[0].cfdi_fecha_timbrado,
                'cfdi_folio_fiscal': atta_facte_brw[0].cfdi_folio_fiscal,
                'cfdi_no_certificado': atta_facte_brw[0].cfdi_no_certificado,
                'cfdi_sello': atta_facte_brw[0].cfdi_sello,
                'cfdi_cadena_original': atta_facte_brw[0].cfdi_cadena_original,
            }        
        return res
        
    def cancel(self, cr, uid, ids, uuid, password, cerCSD, keyCSD, context=None):
        if context is None:
            context = {}
        ir_attch_facte_obj = self.pool.get('ir.attachment.facturae.mx')
        ids_new = ir_attch_facte_obj.search(cr, uid, [('cfdi_folio_fiscal','=',uuid),('create_uid','=',uid)])
        ir_attch_facte_obj.write(cr, uid, ids_new, {'certificate_file': cerCSD, 'certificate_key_file': keyCSD,})
        res = ir_attch_facte_obj.signal_cancel(cr, uid, ids_new, context=context)
        msg = ir_attch_facte_obj.read(cr, uid, ids_new, ['msj'])[0]['msj']
        fecha_cancel = ir_attch_facte_obj.read(cr, uid, ids_new, ['cfdi_fecha_cancelacion'])[0]['cfdi_fecha_cancelacion']
        return {'message': msg, 'status': True, 'cfdi_fecha_cancelacion': fecha_cancel}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
