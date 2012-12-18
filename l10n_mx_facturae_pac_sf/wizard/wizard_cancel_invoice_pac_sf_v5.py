# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Coded by: isaac (isaac@vauxoo.com)
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
from tools.misc import ustr
try:
    from SOAPpy import WSDL
except:
    print "Package SOAPpy missed"
    pass
import time

_form = '''<?xml version="1.0"?>
<form string="Cancel CFDI PAC SF">
    <separator colspan="4" string="File"/>
        <field name='file' nolabel="1" colspan="4"/>
        <newline/>
        <separator colspan="4" string="Message"/>
        <field name='message' nolabel="1" colspan="4"/>
    <separator string="" colspan="4"/>
</form>'''

_fields = {
   'file': {
        'string': 'Name',
        'type': 'binary',
    },
   'message': {
        'string': 'Message',
        'type': 'text',
        'readonly': True,
   },
}

def _get_cancel_invoice_id(self, cr, uid, data, context = {}):
    res = {}
    pool = pooler.get_pool(cr.dbname)
    invoice_obj = pool.get('account.invoice')
    res = invoice_obj._get_file_cancel(cr, uid, data['ids'])
    return res

def _upload_cancel_to_pac(self, cr, uid, data, context ={}):
    res = {}
    pool = pooler.get_pool(cr.dbname)
    invoice_obj = pool.get('account.invoice')
    res = invoice_obj.sf_cancel(cr, uid, data['ids'], context=None)
    return res

class wizard_cancel_invoice_pac_sf_v5(wizard.interface):
    states = {
        'init': {
            'actions': [ _get_cancel_invoice_id ],
            'result': {'type': 'state', 'state':'show_view'},
        },

        'show_view': {
            'actions': [ ],
            'result': {
                'type': 'form',
                'arch': _form,
                'fields': _fields,
                'state': [ ('end', '_Cerrar', 'gtk-cancel', False), ('sf_cancel', '_Cancelar CFDI', 'gtk-ok', True) ]
            }
        },

        'sf_cancel': {
            'actions': [ _upload_cancel_to_pac ],
            'result': {'type': 'state', 'state':'show_view'},
        },
    }
wizard_cancel_invoice_pac_sf_v5('wizard.cancel.invoice.pac.sf.v5')
