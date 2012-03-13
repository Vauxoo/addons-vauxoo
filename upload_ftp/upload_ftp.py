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

import ftplib
import time
import os
from operator import itemgetter
import tempfile
import netsvc
from osv import fields, osv
import base64
from tools.misc import currency
from tools.translate import _
import pooler
import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime

from tools import config

class ir_attachment(osv.osv):
    _inherit = 'ir.attachment'
    
    def binary2file(self, cr, uid, ids, binary_data, file_prefix="", file_suffix=""):
        (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
        f = open( fname, 'wb' )
        f.write( base64.decodestring( binary_data ) )
        f.close()
        os.close( fileno )
        return fname
    
    def file_ftp(self, cr, uid, ids,context={}):
        ftp_id=False
        ftp_obj=pooler.get_pool(cr.dbname).get('ftp.server')
        ftp_id=ftp_obj.search(cr,uid,[('name','!=',False)],context=None)
        if not ftp_id:
            raise osv.except_osv(('Error Servidor ftp!'),('No Existe Servidor ftp Configurado'))
        ftp=ftp_obj.browse(cr,uid,ftp_id,context)[0]
        ftp_servidor = ftp.name
        ftp_usuario  = ftp.ftp_user
        ftp_clave    = ftp.ftp_pwd
        ftp_raiz     = ftp.ftp_raiz
        #atta_obj = pooler.get_pool(cr.dbname).get('ir.attachment')
        archivos=[]
        for id_file in ids:
            if id_file:
                atta_brw = self.browse(cr, uid, [id_file], context)[0]
                file_binary = base64.encodestring(atta_brw.db_datas)
                file=self.binary2file(cr,uid,id_file,file_binary,"ftp","")
                file_name=atta_brw.datas_fname
                archivos.append({'fichero_origen':file,'nombre':file_name})
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
        return True
ir_attachment()

class ftp_server(osv.osv):
    _name='ftp.server'
    
    _columns={
        'name':fields.char('ftp servidor',size=128,required=True),
        'ftp_user':fields.char('ftp suario',size=128,required=True),
        'ftp_pwd':fields.char('ftp clave',size=128,required=True),
        'ftp_raiz':fields.char('ftp raiz',size=128,required=True,help='llenar con siguiente Formato "/done"'),
    }
ftp_server()