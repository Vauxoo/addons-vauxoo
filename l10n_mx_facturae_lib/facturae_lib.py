# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (moylop260@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
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
from tools.translate import _
import tools
import os
import time
import release
import tempfile
import base64

class facturae_certificate_library(osv.osv):
    _name = 'facturae.certificate.library'
    _auto = False
    
    def binary2file(self, cr, uid, ids, binary_data, file_prefix="", file_suffix=""):
        (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
        f = open( fname, 'wb' )
        f.write( base64.decodestring( binary_data ) )
        f.close()
        os.close( fileno )
        return fname
    
    def _generate_pem_fname(self, fname, type='cer', password=None):
        file_b64 = base64.encodestring( open(fname, "r").read() )
        pem_b64 = self._generate_pem_fname(cr, uid, ids, file_b64)
        return pem_b64
    
    def _read_file_attempts(self, fname, max_attempt=6, seconds_delay=0.5):
        fdata = False
        cont = 1
        while True:
            time.sleep( seconds_delay )
            try:
                fdata = open( fname, "r").read()
            except:
                pass
            if fdata or max_attempt < cont:
                break
            cont += 1
        return fdata
    
    def _generate_pem_b64(self, cr, uid, ids, file_b64, type='cer', password=None):
        fname = self.binary2file(cr, uid, [], file_b64, file_prefix="openerp__", file_suffix="."+type)
        
        (fileno_pem, fname_pem) = tempfile.mkstemp('.'+type+'.pem', 'openerp_' + (type or '') + '__facturae__' )
        os.close(fileno_pem)
        pem = ''
        if type == 'cer':
            cmd = 'openssl x509 -inform DER -in %s -outform PEM -pubkey -out %s'%(fname, fname_pem)
            args = tuple( cmd.split(' ') )
            input, output = tools.exec_command_pipe(*args)
            pem = self._read_file_attempts(fname_pem, max_attempt=6, seconds_delay=0.5)
            input.close()
            output.close()
        elif type == 'key':
            (fileno_password, fname_password) = tempfile.mkstemp('.txt', 'openerp_' + (False or '') + '__facturae__' )
            os.close(fileno_password)
            open(fname_password, "w").write( password )
            
            cmd = 'openssl pkcs8 -inform DER -in %s -passin file:%s -out %s'%(fname, fname_password, fname_pem)
            args = tuple(cmd.split(' '))
            input, output = tools.exec_command_pipe(*args)
            pem = self._read_file_attempts(fname_pem, max_attempt=6, seconds_delay=0.5)
            input.close()
            output.close()
            os.unlink(fname_password)
        pem_b64 = base64.encodestring( pem or '') or False
        os.unlink(fname_pem)
        os.unlink(fname)
        return pem_b64
facturae_certificate_library()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
