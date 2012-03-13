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
        atta_obj = self.pool.get('ir.attachment')
        atta_obj.file_ftp(cr,uid,data['files'],context)
        print data,"dataaa"
        return {}


    def _get_files(self,cr, uid, context):
        atta_obj = self.pool.get('ir.attachment')
        atta_ids = atta_obj.search(cr, uid, [('res_id', 'in', context['active_ids'])], context=context)
        res={}
        if atta_ids:
            return atta_ids
        else:
            raise osv.except_osv(('Estado de ftp!'),('Esta factura no ha sido timbrada, por lo que no es posible subir a ftp. No existe .xml'))
        return true

    _columns = {
        'files': fields.many2many('ir.attachment','ftp_wizard_attachment_rel', 'wizard_id', 'attachment_id', 'Attachments'),
    }

    _defaults= {
        'files': _get_files,
    }
wizard_facturae_ftp()

