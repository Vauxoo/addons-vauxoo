# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: el_rodo_1 (rodo@vauxoo.com)
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

from osv import fields, osv
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
import ftplib
from tools.misc import ustr
try:
    from SOAPpy import WSDL
except:
    print "Package SOAPpy missed"
    pass
import time


class wizard_facturae_ftp(osv.osv_memory):
    _name='wizard.facturae.ftp'

    def binary2file(self, cr, uid, ids, binary_data, file_prefix="", file_suffix=""):
        (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
        f = open( fname, 'wb' )
        f.write( base64.decodestring( binary_data ) )
        f.close()
        os.close( fileno )
        return fname

    def invoice_ftp(self, cr, uid, ids, context=None):
        ftp_id=False
        data=self.read(cr,uid,ids)[0]
        context_id=context.get('active_ids',[])
        ftp_obj=self.pool.get('ftp.server')
        ftp_id=ftp_obj.search(cr,uid,[('name','!=',False)],context=None)
        if not ftp_id:
            raise osv.except_osv(('Error Servidor ftp!'),('No Existe Servidor ftp Configurado'))
        ftp=ftp_obj.browse(cr,uid,ftp_id,context)[0]
        ftp_servidor = ftp.name
        ftp_usuario  = ftp.ftp_user
        ftp_clave    = ftp.ftp_pwd
        ftp_raiz     = ftp.ftp_raiz
        atta_obj = self.pool.get('ir.attachment')
        atta_id_xml = atta_obj.search(cr, uid, [('res_id', '=', context['active_id']), ('datas_fname', 'ilike', '%.xml')], context=context)
        atta_id_pdf = atta_obj.search(cr, uid, [('res_id', '=', context['active_id']), ('datas_fname', 'ilike', '%.pdf')], context=context)
        archivos=[]
        if atta_id_xml:
            atta_brw = atta_obj.browse(cr, uid, atta_id_xml, context)[0]
            inv_xml = base64.encodestring(atta_brw.db_datas)
            xml=self.binary2file(cr,uid,ids,inv_xml,"",".xml")
            xml_name=atta_brw.datas_fname
            archivos.append({'fichero_origen':xml,'nombre':xml_name})
        else:
            raise osv.except_osv(('Error xml!'),('Esta factura no ha sido timbrada, por lo que no es posible subir a ftp. No existe .xml'))
        if atta_id_pdf:
            atta_brw = atta_obj.browse(cr, uid, atta_id_pdf, context)[0]
            inv_pdf = base64.encodestring(atta_brw.db_datas)
            pdf=str(self.binary2file(cr,uid,ids,inv_pdf,"",".pdf"))
            pdf_name=atta_brw.datas_fname
            archivos.append({'fichero_origen':pdf,'nombre':pdf_name})
        else:
            raise osv.except_osv(('Error pdf!'),('Esta factura no ha sido timbrada, por lo que no es posible subir a ftp. No existe .xml'))
        for a in archivos:
            try:
                s = ftplib.FTP(ftp_servidor, ftp_usuario, ftp_clave)
                f = open((a['fichero_origen']), 'rb')
                s.cwd(ftp_raiz)
                s.storbinary('STOR ' + (a['nombre']), f)
                f.close()
                s.quit()
            except:
                raise osv.except_osv(('Error Configuracion ftp!'),('Revisar Informacion de Servidor ftp'))
        return {}


    def _get_file_xml(self,cr, uid, context):
        atta_obj = self.pool.get('ir.attachment')
        atta_id = atta_obj.search(cr, uid, [('res_id', '=', context['active_id']), ('name', 'ilike', '%.xml')], context=context)
        res={}
        if atta_id:
            atta_brw = atta_obj.browse(cr, uid, atta_id, context)[0]
            inv_xml = base64.encodestring(atta_brw.db_datas)

        else:
            inv_xml = False
            raise osv.except_osv(('Estado de ftp!'),('Esta factura no ha sido timbrada, por lo que no es posible subir a ftp. No existe .xml'))
        return inv_xml

    def _get_file_pdf(self,cr, uid, context):
        atta_obj = self.pool.get('ir.attachment')
        atta_id = atta_obj.search(cr, uid, [('res_id', '=', context['active_id']), ('name', 'ilike', '%')], context=context)
        res={}
        if atta_id:
            atta_brw = atta_obj.browse(cr, uid, atta_id, context)[0]
            inv_xml = base64.encodestring(atta_brw.db_datas)

        else:
            inv_xml = False
            raise osv.except_osv(('Estado de ftp!'),('Esta factura no ha sido timbrada, por lo que no es posible subir a ftp. No existe .pdf'))
        return inv_xml

    _columns = {
        'file_xml': fields.binary('File xml', readonly=True),
        'file_pdf': fields.binary('File pdf', readonly=True),
        'message': fields.text('text'),

    }

    _defaults= {
        'message': 'Seleccione el botón ftp',
        'file_xml': _get_file_xml,
        'file_pdf': _get_file_pdf,
    }
wizard_facturae_ftp()

