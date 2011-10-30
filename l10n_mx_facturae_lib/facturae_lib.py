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
    """
    def set_global_fname_der(self, cer_der_b64=None, key_der_b64=None, password_der=None):
        self._fname_cer_der = self.binary2file(None, None, [], cer_der_b64, file_prefix='openerp__' + (False or '') + '__ssl__', file_suffix='.der.cer')
        self._fname_key_der = self.binary2file(None, None, [], key_der_b64, file_prefix='openerp__' + (False or '') + '__ssl__', file_suffix='.der.key')
        password_der_b64 = base64.encodestring(password_der)
        self._fname_password_der = self.binary2file(None, None, [], password_der_b64, file_prefix='openerp__' + (False or '') + '__ssl__', file_suffix='.der.txt')
    
    def delete_global_fname_der(self):
        os.unlink( self._fname_cer_der )
        os.unlink( self._fname_key_der )
        os.unlink( self._fname_password_der )
    
    def set_global_fname_pem(self, cer_pem_b64=None, key_pem_b64=None):
        self._fname_cer_pem = self.binary2file(None, None, [], cer_pem_b64, file_prefix='openerp__' + (False or '') + '__ssl__', file_suffix='.pem.cer')
        self._fname_key_pem = self.binary2file(None, None, [], key_pem_b64, file_prefix='openerp__' + (False or '') + '__ssl__', file_suffix='.pem.key')
    
    def delete_global_fname_pem(self):
        os.unlink( self._fname_cer_pem )
        os.unlink( self._fname_key_pem )
    
    def set_global_fname_temp(self, fname_temp=None):
        if not fname_temp:
            self._fname_temp = self.binary2file(None, None, [], '', file_prefix='openerp__' + (False or '') + '__ssl__', file_suffix='.temp.txt')
        else:
            self._fname_temp = fname_temp
    
    def delete_global_fname_temp(self):
        os.unlink( self._fname_temp )
    """
    def b64str_to_tempfile(self, b64_str="", file_suffix="", file_prefix=""):
        (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
        f = open( fname, 'wb' )
        f.write( base64.decodestring( b64_str ) )
        f.close()
        os.close( fileno )
        return fname
    
    def binary2file(self, cr=False, uid=False, ids=[], binary_data=False, file_prefix="", file_suffix=""):
        (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
        f = open( fname, 'wb' )
        f.write( base64.decodestring( binary_data ) )
        f.close()
        os.close( fileno )
        return fname
    
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
    
    def _transform_der_to_pem(self, fname_der, fname_out, fname_password_der=None, type_der='cer'):
        """"
        @type_der cer or key
        """
        cmd = ''
        result = ''
        if type_der == 'cer':
            cmd = 'openssl x509 -inform DER -outform PEM -in %s -pubkey -out %s'%( fname_der, fname_out )
        elif type_der == 'key':
            cmd = 'openssl pkcs8 -inform DER -outform PEM -in %s -passin file:%s -out %s'%( fname_der, fname_password_der, fname_out )
        if cmd:
            args = tuple( cmd.split(' ') )
            input, output = tools.exec_command_pipe(*args)
            result = self._read_file_attempts(fname_out, max_attempt=3, seconds_delay=0.5)
            input.close()
            output.close()
        return result
    
    def _get_param_serial(self, fname, fname_out=None, type='DER'):
        result = self._get_params(fname, params=['serial'], fname_out=fname_out, type=type)
        result = result and result.replace('serial=', '').replace('33', 'B').replace('3', '').replace('B', '3').replace(' ', '').replace('\r', '').replace('\n', '').replace('\r\n', '') or ''
        return result
        
    def _get_param_dates(self, fname, fname_out=None, date_fmt_return='%Y-%m-%d %H:%M:%S', type='DER'):
        result_dict = self._get_params_dict(fname, params=['dates'], fname_out=fname_out, type=type)
        translate_key = {
            'notAfter': 'enddate',
            'notBefore': 'startdate',
        }
        result2 = {}
        if result_dict:
            date_fmt_src = "%b %d %H:%M:%S %Y GMT"
            for key in result_dict.keys():
                date = result_dict[key]
                date_obj = time.strptime(date, date_fmt_src)
                date_fmt = time.strftime(date_fmt_return, date_obj)
                result2[ translate_key[key] ] = date_fmt
        return result2 or None
    
    def _get_params_dict(self, fname, params=None, fname_out=None, type='DER'):
        result = self._get_params(fname, params, fname_out, type)
        result = result.replace('\r\n', '\n').replace('\r', '\n')#.replace('\n', '\n)
        result = result.rstrip('\n').lstrip('\n').rstrip(' ').lstrip(' ')
        params = result.split('\n')
        params_dict = {}
        for param in params:
            key,value = param.split('=')
            params_dict[key] = value
        return params_dict

    def _get_params(self, fname, params=None, fname_out=None, type='DER'):
        """
        @params: list [noout serial startdate enddate subject issuer dates]
        @type: str DER or PEM
        """
        #params = "-startdate -enddate"
        #params.split(' ')
        cmd_params = ' -'.join(params)
        cmd_params = cmd_params and '-' + cmd_params or ''
        #print "cmd_params",cmd_params
        #cmd = "openssl x509 -inform %s -noout %s -in %s -out %s"%(type, cmd_params, fname, fname_out)
        cmd = "openssl x509 -inform %s -in %s -noout %s -out %s"%( type, fname, cmd_params, fname_out )
        #print "cmd",cmd
        args = tuple( cmd.split(' ') )
        input, output = tools.exec_command_pipe(*args)
        result = output.read()
        input.close()
        output.close()
        return result
        
    ##############TODAS ESTAS FUNCIONES QUEDARAN EN DESUSO###
    def _____get_serial(self, fname, fname_out=None, type='DER'):
        """
        @type: DER or PEM
        """
        type = type and type.upper() or ''
        cmd = "openssl x509 -inform %s -in %s -serial -noout -out %s"%(type, fname, fname_out)
        args = tuple( cmd.split(' ') )
        input, output = tools.exec_command_pipe(*args)
        #no_certificado = self._read_file_attempts(fname_out, max_attempt=6, seconds_delay=0.5)
        result = output.read()
        result = result.replace('serial=', '').replace('33', 'B').replace('3', '').replace('B', '3').replace(' ', '').replace('\r', '').replace('\n', '').replace('\r\n', '')
        input.close()
        output.close()
        return result
    def _generate_pem_fname(self, fname, type='cer', password=None):
        file_b64 = base64.encodestring( open(fname, "r").read() )
        pem_b64 = self._generate_pem_fname(cr, uid, ids, file_b64)
        return pem_b64
    
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
    
    def _________get_serial(self, file_b64, pem=True):
        fname = self.binary2file(False, False, [], file_b64, file_prefix="openerp__", file_suffix=".pem")
        (fileno_tmp, fname_tmp) = tempfile.mkstemp('.txt', 'openerp_' + ('serial' or '') + '__facturae__')
        os.close(fileno_tmp)
        cmd = "openssl x509 -in %s -serial -noout -out %s"%(fname, fname_tmp)
        args = tuple( cmd.split(' ') )
        input, output = tools.exec_command_pipe(*args)
        #no_certificado = self._read_file_attempts(fname_tmp, max_attempt=6, seconds_delay=0.5)
        no_certificado_hex = output.read()
        no_certificado = no_certificado_hex.replace('serial=', '').replace('33', 'B').replace('3', '').replace('B', '3').replace(' ', '').replace('\r', '').replace('\n', '').replace('\r\n', '')
        input.close()
        output.close()
        os.unlink(fname)
        os.unlink(fname_tmp)
        return no_certificado
    
    def _get_startdate_enddate(self, file_b64, pem=False):
        fname = self.binary2file(False, False, [], file_b64, file_prefix="openerp__", file_suffix=".cer")
        (fileno_tmp, fname_tmp) = tempfile.mkstemp('.txt', 'openerp_' + ('serial' or '') + '__facturae__')
        os.close(fileno_tmp)
        cmd = "openssl x509 -inform DER -noout -startdate -enddate -in %s -out %s"%( fname, fname_tmp)
        args = tuple( cmd.split(' ') )
        input, output = tools.exec_command_pipe(*args)
        #res = self._read_file_attempts(fname_tmp, max_attempt=6, seconds_delay=0.5)
        #print "res",res
        res = output.read()
        input.close()
        output.close()
        os.unlink(fname)
        os.unlink(fname_tmp)
        return res
facturae_certificate_library()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
