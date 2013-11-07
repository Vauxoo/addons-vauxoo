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

from openerp import pooler
from openerp.tools.translate import _

import base64
import time

_form = """<?xml version="1.0"?>
<form string="Factura Electronica XML">
    <label string="Deseas obtener la Factura Electronica XML?"/>
    <newline/>
    <label string="NOTA: Recuerda que si ya existe un XML adjunto, te mostrara \
    este xml anterior.\nPara regenerarlo, tendra que borrar el anterior."/>
</form>"""

_fields = {
}


def _get_invoice_facturae_xml(self, cr, uid, data, context=None):
    if context is None:
        context = {}
    # context.update( {'date': data['form']['date']} )
    pool = pooler.get_pool(cr.dbname)
    invoice_obj = pool.get('account.invoice')
    ids = data['ids']
    id = ids[0]
    invoice = invoice_obj.browse(cr, uid, [id], context=context)[0]
    fname_invoice = invoice.fname_invoice and invoice.fname_invoice + \
        '.xml' or ''
    aids = pool.get('ir.attachment').search(cr, uid, [('datas_fname', '=',
        invoice.fname_invoice+'.xml'), (
        'res_model', '=', 'account.invoice'), ('res_id', '=', id)])
    xml_data = ""
    if aids:
        brow_rec = pool.get('ir.attachment').browse(cr, uid, aids[0])
        if brow_rec.datas:
            xml_data = base64.decodestring(brow_rec.datas)
    else:
        fname, xml_data = invoice_obj._get_facturae_invoice_xml_data(
            cr, uid, ids, context=context)  # TODO: Del this line
        # pool.get('ir.attachment').create(cr, uid, {
            #'name': fname_invoice,
            #'datas': base64.encodestring(xml_data),
            #'datas_fname': fname_invoice,
            #'res_model': 'account.invoice',
            #'res_id': invoice.id,
            #}, context=context
        #)
        id = invoice_obj._attach_invoice(cr, uid, ids, context=context)

    fdata = base64.encodestring(xml_data)
    return {'facturae': fdata, 'facturae_fname': fname_invoice, }

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


class wizard_invoice_facturae_xml(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form',
                       'arch': _form,
                       'fields': _fields,
                       'state': [('end', 'Cancel'), ('export', 'Export', 'gtk-ok')]}
        },
        'init': {
            'actions': [_get_invoice_facturae_xml],
            'result': {'type': 'form',
                       'arch': end_form,
                       'fields': end_fields,
                       'state': [('end', 'Ok', 'gtk-ok')]}
        }

    }
wizard_invoice_facturae_xml('wizard.invoice.facturae.xml')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
