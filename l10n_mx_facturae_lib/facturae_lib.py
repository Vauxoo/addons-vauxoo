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

from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _

import os
import sys
import time
import tempfile
import base64
import binascii
import logging
_logger = logging.getLogger(__name__)
from l10n_mx_facturae_lib import facturae_lib

all_paths = tools.config["addons_path"].split(",")
for my_path in all_paths:
    if os.path.isdir(os.path.join(my_path, 'l10n_mx_facturae_base', 'depends_app')):
        openssl_path = my_path and os.path.join(my_path, 'l10n_mx_facturae_base', 'depends_app', u'openssl_win') or ''
        xsltproc_path = my_path and os.path.join(my_path, 'l10n_mx_facturae_base', 'depends_app', u'xsltproc_win') or ''
        xmlstarlet_path = my_path and os.path.join(my_path, 'l10n_mx_facturae_base', 'depends_app', u'xmlstarlet_win') or ''

def exec_command_pipe(*args):
    # Agregue esta funcion, ya que con la nueva funcion original, de tools no funciona
# TODO: Hacer separacion de argumentos, no por espacio, sino tambien por "
# ", como tipo csv, pero separator espace & delimiter "
    cmd = ' '.join(args)
    if os.name == "nt":
        cmd = cmd.replace(
            '"', '')  # provisionalmente, porque no funcionaba en win32
    return os.popen2(cmd, 'b')

if os.name == "nt":
    app_xsltproc = 'xsltproc.exe'
    app_openssl = 'openssl.exe'
    app_xmlstarlet = 'xmlstarlet.exe'
else:
    app_xsltproc = 'xsltproc'
    app_openssl = 'openssl'
    app_xmlstarlet = 'xmlstarlet'

app_openssl_fullpath = os.path.join(openssl_path, app_openssl)
if not os.path.isfile(app_openssl_fullpath):
    app_openssl_fullpath = tools.find_in_path(app_openssl)
    if not os.path.isfile(app_openssl_fullpath):
        app_openssl_fullpath = False
        _logger.warning('Install openssl "sudo apt-get install openssl" to use l10n_mx_facturae_lib module.')

app_xsltproc_fullpath = os.path.join(xsltproc_path, app_xsltproc) or False
try:
    if not os.path.isfile(app_xsltproc_fullpath):
        app_xsltproc_fullpath = tools.find_in_path(app_xsltproc) or False
        if not os.path.isfile(app_xsltproc_fullpath):
            app_xsltproc_fullpath = False
            _logger.warning('Install xsltproc "sudo apt-get install xsltproc" to use l10n_mx_facturae_lib module.')
except Exception, e:
    _logger.warning("Install xsltproc 'sudo apt-get install xsltproc' to use l10n_mx_facturae_lib module.")

app_xmlstarlet_fullpath = os.path.join(xmlstarlet_path, app_xmlstarlet)
if not os.path.isfile( app_xmlstarlet_fullpath ):
    app_xmlstarlet_fullpath = tools.find_in_path( app_xmlstarlet )
    if not app_xmlstarlet_fullpath:
        app_xmlstarlet_fullpath = False
        _logger.warning('Install xmlstarlet "sudo apt-get install xmlstarlet" to use l10n_mx_facturae_lib module.')

def library_openssl_xsltproc_xmlstarlet(self, cr, uid, ids, context=None):
    if context is None:
        context = {}
    msj = ''
    app_openssl_fullpath = os.path.join(openssl_path, app_openssl)
    if not os.path.isfile(app_openssl_fullpath):
        app_openssl_fullpath = tools.find_in_path(app_openssl)
        if not os.path.isfile(app_openssl_fullpath):
            app_openssl_fullpath = False
            _logger.warning('Install openssl "sudo apt-get install openssl" to use l10n_mx_facturae_lib module.')
            msj += 'Install openssl "sudo apt-get install openssl" to use l10n_mx_facturae_lib module.'
    
    app_xsltproc_fullpath = os.path.join(xsltproc_path, app_xsltproc) or False
    if not os.path.isfile(app_xsltproc_fullpath):
        app_xsltproc_fullpath = tools.find_in_path(app_xsltproc) or False
        try:
            if not os.path.isfile(app_xsltproc_fullpath):
                app_xsltproc_fullpath = False
                _logger.warning("Install xsltproc 'sudo apt-get install xsltproc' to use l10n_mx_facturae_lib module.")
                msj =  "Install xsltproc 'sudo apt-get install xsltproc' to use l10n_mx_facturae_lib module."
        except Exception, e:
            _logger.warning("Install xsltproc 'sudo apt-get install xsltproc' to use l10n_mx_facturae_lib module.")
            msj +=  "Install xsltproc 'sudo apt-get install xsltproc' to use l10n_mx_facturae_lib module."

    app_xmlstarlet_fullpath = os.path.join(xmlstarlet_path, app_xmlstarlet)
    if not os.path.isfile( app_xmlstarlet_fullpath ):
        app_xmlstarlet_fullpath = tools.find_in_path( app_xmlstarlet )
        if not app_xmlstarlet_fullpath:
            app_xmlstarlet_fullpath = False
            _logger.warning('Install xmlstarlet "sudo apt-get install xmlstarlet" to use l10n_mx_facturae_lib module.')
            msj += 'Install xmlstarlet "sudo apt-get install xmlstarlet" to use l10n_mx_facturae_lib module.'
    return msj, app_xsltproc_fullpath, app_openssl_fullpath, app_xmlstarlet_fullpath
        

class facturae_certificate_library(osv.Model):
    _name = 'facturae.certificate.library'
    _auto = False
    # Agregar find subpath

    def b64str_to_tempfile(self, cr, uid, ids, b64_str=None, file_suffix=None, file_prefix=None, context=None):
        """
        @param b64_str : Text in Base_64 format for add in the file
        @param file_suffix : Sufix of the file
        @param file_prefix : Name of file in TempFile
        """
        if context is None:
            context = {}
        (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
        f = open(fname, 'wb')
        f.write(base64.decodestring(b64_str or ''))
        f.close()
        os.close(fileno)
        return fname

    def _read_file_attempts(self, file_obj, max_attempt=12, seconds_delay=0.5):
        """
        @param file_obj : Object with the path of the file, more el mode
            of the file to create (read, write, etc)
        @param max_attempt : Max number of attempt
        @param seconds_delay : Seconds valid of delay
        """
        fdata = False
        cont = 1
        while True:
            time.sleep(seconds_delay)
            try:
                fdata = file_obj.read()
            except:
                pass
            if fdata or max_attempt < cont:
                break
            cont += 1
        return fdata

    def _transform_der_to_pem(self, fname_der, fname_out,
        fname_password_der=None, type_der='cer'):
        """
        @param fname_der : File.cer configurated in the company
        @param fname_out : Information encrypted in Base_64from certificate
            that is send
        @param fname_password_der : File that contain the password configurated
            in this Certificate
        @param type_der : cer or key
        """
        if not app_openssl_fullpath:
            raise osv.except_osv(_("Error!"), _(
                "Failed to find in path '%s' app. This app is required for sign Mexican Electronic Invoice"%(app_openssl) ))
        cmd = ''
        result = ''
        if type_der == 'cer':
            cmd = '"%s" x509 -inform DER -outform PEM -in "%s" -pubkey -out "%s"' % (
                app_openssl_fullpath, fname_der, fname_out)
        elif type_der == 'key':
            cmd = '"%s" pkcs8 -inform DER -outform PEM -in "%s" -passin file:%s -out "%s"' % (
                app_openssl_fullpath, fname_der, fname_password_der, fname_out)
        if cmd:
            args = tuple(cmd.split(' '))
            # input, output = tools.exec_command_pipe(*args)
            input, output = exec_command_pipe(*args)
            result = self._read_file_attempts(open(fname_out, "r"))
            input.close()
            output.close()
        return result

    def _get_param_serial(self, cr, uid, ids, fname, fname_out=None, type='DER', context=None):
        """
        @param fname : File.PEM with the information of the certificate
        @param fname_out : File.xml that is send
        """
        if context is None:
            context = {}
        result = self._get_params(cr, uid, ids, fname, params=['serial'], 
                                    fname_out=fname_out, type=type)
        result = result and result.replace('serial=', '').replace(
            '33', 'B').replace('3', '').replace('B', '3').replace(
            ' ', '').replace('\r', '').replace('\n', '').replace('\r\n', '') or ''
        return result

    def _transform_xml(self, cr, uid, ids, fname_xml, fname_xslt, fname_out, context=None):
        """
        @param fname_xml : Path and name of the XML of Facturae
        @param fname_xslt : Path where is located the file 'Cadena Original'.xslt
        @param fname_out : Path and name of the file.xml that is send to sign
        """
        if context is None:
            context = {}
        msj, app_xsltproc_fullpath, app_openssl_fullpath, app_xmlstarlet_fullpath = facturae_lib.library_openssl_xsltproc_xmlstarlet(cr, uid, ids, context)
        if not app_xsltproc_fullpath:
            raise osv.except_osv(_("Error!"), _(
                "Failed to find in path '%s' app. This app is required for sign Mexican Electronic Invoice"%(app_xsltproc) ))
        cmd = '"%s" "%s" "%s" >"%s"' % (
            app_xsltproc_fullpath, fname_xslt, fname_xml, fname_out)
        args = tuple(cmd.split(' '))
        input, output = exec_command_pipe(*args)
        result = self._read_file_attempts(open(fname_out, "r"))
        input.close()
        output.close()
        return result

    def _get_param_dates(self, cr, uid, ids, fname, fname_out=None,
        date_fmt_return='%Y-%m-%d %H:%M:%S', type='DER', context=None):
        """
        @param fname : File.cer with the information of the certificate
        @params fname_out : Path and name of the file.txt with info encrypted
        @param date_fmt_return : Format of the date used
        @param type : Type of file
        """
        if context is None:
            context = {}
        result_dict = self._get_params_dict(cr, uid, ids, fname, params=[
                                    'dates'], fname_out=fname_out, type=type)
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
                result2[translate_key[key]] = date_fmt
        return result2

    def _get_params_dict(self, cr, uid, ids, fname, params=None, fname_out=None, type='DER', context=None):
        """
        @param fname : File.cer with the information of the certificate
        @param params : List of params used for this function
        @param fname_out : Path and name of the file.txt with info encrypted
        @param type : Type of file
        """
        if context is None:
            context = {}
        result = self._get_params(cr, uid, ids, fname, params, fname_out, type)
        result = result.replace('\r\n', '\n').replace(
            '\r', '\n')  # .replace('\n', '\n)
        result = result.rstrip('\n').lstrip('\n').rstrip(' ').lstrip(' ')
        result_list = result.split('\n')
        params_dict = {}
        for result_item in result_list:
            if result_item:
                key, value = result_item.split('=')
                params_dict[key] = value
        return params_dict

    def _get_params(self, cr, uid, ids, fname, params=None, fname_out=None, type='DER', context=None):
        """
        @params: list [noout serial startdate enddate subject issuer dates]
        @type: str DER or PEM
        """
        if context is None:
            context = {}
        msj, app_xsltproc_fullpath, app_openssl_fullpath, app_xmlstarlet_fullpath = facturae_lib.library_openssl_xsltproc_xmlstarlet(cr, uid, ids, context)
        if not app_openssl_fullpath:
            raise osv.except_osv(_("Error!"), _(
                "Failed to find in path '%s' app. This app is required for sign Mexican Electronic Invoice"%(app_openssl) ))
        cmd_params = ' -'.join(params)
        cmd_params = cmd_params and '-' + cmd_params or ''
        cmd = '"%s" x509 -inform "%s" -in "%s" -noout "%s" -out "%s"' % (
            app_openssl_fullpath, type, fname, cmd_params, fname_out)
        args = tuple(cmd.split(' '))
        # input, output = tools.exec_command_pipe(*args)
        input, output = exec_command_pipe(*args)
        result = self._read_file_attempts(output)
        input.close()
        output.close()
        return result

    def _sign(self, cr, uid, ids, fname, fname_xslt, fname_key, fname_out, encrypt='sha1',
        type_key='PEM', context=None):
        """
         @params fname : Path and name of the XML of Facturae
         @params fname_xslt : Path where is located the file 'Cadena Original'.xslt
         @params fname_key : Path and name of the file.pem with data of the key
         @params fname_out : Path and name of the file.txt with info encrypted
         @params encrypt : Type of encryptation for file
         @params type_key : Type of KEY
        """
        if context is None:
            context = {}
        msj, app_xsltproc_fullpath, app_openssl_fullpath, app_xmlstarlet_fullpath = \
                    facturae_lib.library_openssl_xsltproc_xmlstarlet(cr, uid, ids, context)
        result = ""
        cmd = ''
        if type_key == 'PEM':
            if not app_xsltproc_fullpath:
                raise osv.except_osv(_("Error!"), _(
                    "Failed to find in path '%s' app. This app is required for sign Mexican Electronic Invoice"%(app_xsltproc) ))
            cmd = '"%s" "%s" "%s" | "%s" dgst -%s -sign "%s" | "%s" enc -base64 -A -out "%s"' % (
                app_xsltproc_fullpath, fname_xslt, fname, app_openssl_fullpath,
                    encrypt, fname_key, app_openssl_fullpath, fname_out)
        elif type_key == 'DER':
            # TODO: Dev for type certificate DER
            pass
        if cmd:
            print cmd, 'cmd'*20
            input, output = exec_command_pipe(cmd)
            result = self._read_file_attempts(open(fname_out, "r"))
            input.close()
            output.close()
        return result

    def check_xml_scheme(self, cr, uid, ids, fname_xml, fname_scheme, fname_out, type_scheme="xsd",
                            context=None):
        #xmlstarlet val -e --xsd cfdv2.xsd cfd_example.xml
        if context is None:
            context = {}
        msj, app_xsltproc_fullpath, app_openssl_fullpath, app_xmlstarlet_fullpath = facturae_lib.library_openssl_xsltproc_xmlstarlet(cr, uid, ids, context)
        if app_xmlstarlet_fullpath:
            cmd = ''
            if type_scheme == 'xsd':
                cmd = '"%s" val -e --%s "%s" "%s" 1>"%s" 2>"%s"'%(app_xmlstarlet_fullpath, type_scheme, fname_scheme, fname_xml, fname_out+"1", fname_out)
            if cmd:
                args = tuple( cmd.split(' ') )
                input, output = exec_command_pipe(*args)
                result = self._read_file_attempts( open(fname_out, "r") )
                input.close()
                output.close()
        else:
            _logger.warning("Failed to find in path 'xmlstarlet' app. Can't validate xml structure. You should make a manual check to xml file.")
            result = ""
        return result

    # Funciones en desuso
    def binary2file(self, cr=False, uid=False, ids=[], binary_data=False,
        file_prefix="", file_suffix=""):
        """
        @param binary_data : Field binary with the information of certificate
            of the company
        @param file_prefix : Name to be used for create the file with the
            information of certificate
        @file_suffix : Sufix to be used for the file that create in this function
        """
        (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
        f = open(fname, 'wb')
        f.write(base64.decodestring(binary_data))
        f.close()
        os.close(fileno)
        return fname

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
