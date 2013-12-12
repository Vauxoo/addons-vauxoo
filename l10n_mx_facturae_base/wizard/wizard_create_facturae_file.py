# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Launchpad Project Manager for Publication: Nhomar Hernandez - nhomar@vauxoo.com
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
from openerp import pooler, tools, netsvc

import wizard
import base64
import time

_form = """<?xml version="1.0"?>
<form string="Create facturae">
    <label string="Do you want to Create facturae?"/>
    <newline/>
    <field name="date"/>
</form>"""

_fields = {
    'date': {'string': 'Mes a reportar', 'type': 'date'}
}

# end_form = """<?xml version="1.0"?>
#<form string="Create facturae">
    #<label string="en desarrollo"/>
#</form>"""
# end_fields = {}


def _create_facturae_file(self, cr, uid, data, context=None):
    if context is None:
        context = {}
    context.update({'date': data['form']['date']})
    pool = pooler.get_pool(cr.dbname)
    invoice_obj = pool.get('account.invoice')
    ids = data['ids']
    if len(ids) == 1:
        fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(
            cr, uid, ids, context=context)
    else:
        fname = "facturae_mensual.txt"
        xml_data, fname = invoice_obj._get_facturae_invoice_txt_data(
            cr, uid, ids, context=context)
        # fname = "1" + rfc + time.strftime('%m-%Y', time.strptime(data['form']['date'], '%Y-%m-%d')) + '.txt'
    # print xml_data
    # print dict_datas
    file = base64.encodestring(xml_data)
    return {'facturae': file, 'facturae_fname': fname, }

end_form = """<?xml version="1.0"?>
<form string="facturae export">
    <field name="facturae" filename="facturae_fname"/>
    <field name="facturae_fname" invisible="1"/>
    <field name="note" colspan="4" nolabel="1"/>
</form>"""

end_fields = {
    'facturae': {
        'string': 'facturae file',
        'type': 'binary',
        'required': False,
        'readonly': True,
    },
    'facturae_fname': {'string': 'File name', 'type': 'char', 'size': 64},
    'note': {'string': 'Log', 'type': 'text'},
}


class wizard_create_facturae_file(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form',
                       'arch': _form,
                       'fields': _fields,
                       'state': [('end', 'Cancel'), ('export', 'Export', 'gtk-ok')]}
        },
        'export': {
            'actions': [_create_facturae_file],
            'result': {'type': 'form',
                       'arch': end_form,
                       'fields': end_fields,
                       'state': [('end', 'Ok', 'gtk-ok')]}
        }

    }
wizard_create_facturae_file('wizard.create.facturae.file')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
