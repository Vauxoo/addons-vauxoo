# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
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
import base64
import StringIO
import csv
import tempfile
import os
import sys
import codecs
import ftplib

_form = """<?xml version="1.0"?>
<form string="Invoice To ftp">
    <field name='files' nolabel="1" colspan="4"/>
</form>
"""
_fields ={
        'files': {'string':'Files', 'type':'many2many','relation': 'ir.attachment'},
    }


def binary2file(self, cr, uid, ids, binary_data, file_prefix="", file_suffix=""):
    (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
    f = open( fname, 'wb' )
    f.write( base64.decodestring( binary_data ) )
    f.close()
    os.close( fileno )
    return fname

def invoice_ftp(self, cr, uid, data,context={}):
    atta_obj = pooler.get_pool(cr.dbname).get('ir.attachment')
    atta_obj.file_ftp(cr,uid,data['form']['files'][0][2],context)
    return data


def _get_files(self, cr, uid, data, context):
    atta_obj = pooler.get_pool(cr.dbname).get('ir.attachment')
    atta_ids=atta_obj.search(cr, uid, [('res_id', 'in', data['ids']),('res_model','=', data['model'])], context=context)
    res={}
    if atta_ids:
        data['form']['files'] =atta_ids
    else:
        data['form']['files'] = False
        raise osv.except_osv(('Estado de ftp!'),('Esta factura no ha sido timbrada, por lo que no es posible subir a ftp. No existe .xml'))
    return data['form']


class wizard_facturae_ftp(wizard.interface):
    states = {
        'init' : {
            'actions' : [_get_files],
            'result' : {'type' : 'form',
                    'arch' : _form,
                    'fields' : _fields,
                    'state' : [('end', 'Cancel'),('aceptar', 'Aceptar') ]}
        },
        'aceptar' : {
            'actions' : [invoice_ftp],
            'result' : {'type' : 'state',
                    'state' : 'end'
            },
        },
    }
wizard_facturae_ftp('wizard.facturae.ftp')

