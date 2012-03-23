# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Financed by: http://www.sfsoluciones.com (aef@sfsoluciones.com)
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
import xml.dom.minidom
from datetime import datetime, timedelta
from tools.misc import ustr
try:
    from SOAPpy import WSDL
except:
    print "Package SOAPpy missed"
    pass
import time
####Agregar traducciones
_form = '''<?xml version="1.0"?>
<form string="Export invoice Solucion Factible">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
        <field name="file"/>
        <newline/>
        <field name="msg" nolabel="1" colspan="3"/>
    </group>
</form>'''
_fields  = {
    'name': {
        'string': 'Name',
        'type': 'char',
        'size': 64,
    },
    'fname': {
        'string': 'Name',
        'type': 'char',
        'size': 64,
    },
    'file': {
        'string': 'File',
        'type': 'binary',
        'required': True,
        'readonly': True,
    },
    'msg': {
        'string' : 'msg',
        'type': 'text',
        'readonly': True,
    },
}

def _get_invoice_id(self, cr, uid, data, context = {}):
    res = {}
    pool = pooler.get_pool(cr.dbname)
    invoice_obj = pool.get('account.invoice')
    res = invoice_obj._get_file(cr, uid, data['ids'])
    return res

def _upload_to_pac(self, cr, uid, data, context ={}):
    res = {}
    pool = pooler.get_pool(cr.dbname)
    invoice_obj = pool.get('account.invoice')
    res = invoice_obj._upload_ws_file(cr, uid, data['ids'])
    return res

class wizard_export_invoice_pac_sf(wizard.interface):
    states = {
        'init': {
            'actions': [ _get_invoice_id ],
            'result': {'type': 'state', 'state':'show_view'},
        },

        'show_view': {
            'actions': [ ],
            'result': {
                'type': 'form',
                'arch': _form,
                'fields': _fields,
                'state': [ ('end', '_Cerrar', 'gtk-cancel', False), ('upload_ws', '_Subir Archivo', 'gtk-ok', True) ]
            }
        },

        'upload_ws': {
            'actions': [ _upload_to_pac ],
            'result': {'type': 'state', 'state':'show_view'},
        },
    }
wizard_export_invoice_pac_sf('wizard.export.invoice.pac.sf')
