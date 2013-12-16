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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools, netsvc

import wizard
import base64
import time
import datetime
from dateutil.relativedelta import relativedelta


def _get_month_selection(self=False):
    months_selection = [
        (1, 'Enero'),
        (2, 'Febrero'),
        (3, 'Marzo'),
        (4, 'Abril'),
        (5, 'Mayo'),
        (6, 'Junio'),
        (7, 'Julio'),
        (8, 'Agosto'),
        (9, 'Septiembre'),
        (10, 'Octubre'),
        (11, 'Noviembre'),
        (12, 'Diciembre'),
    ]
    return months_selection

_form = """<?xml version="1.0"?>
<form string="Factura Electronica - Reporte Mensual TXT">
    <separator string="FILTROS PARA EXTRAER FACTURAS" colspan="4"/>
    <separator string="Filtro por Mes" colspan="4"/>
    <field name="month"/>
    <field name="year"/>
    <separator string="Filtro por fechas" colspan="4"/>
    <field name="date_start"/>
    <field name="date_end"/>
    <separator string="FACTURAS" colspan="4"/>
    <field name="invoice_ids" colspan="4"/>
</form>"""

_fields = {
    'month': {'string': u'Mes', 'type': 'selection',
        'selection': _get_month_selection(), 'default': int(time.strftime("%m")) - 1},
    'year': {'string': u'Año', 'type': 'integer', 'default': int(time.strftime("%Y"))},
    'date_start': {'string': u'Fecha Inicial', 'type': 'datetime',
        'default': (datetime.datetime.strptime(time.strftime('%Y-%m-01 00:00:00'),
        '%Y-%m-%d 00:00:00') - relativedelta(months=1)).strftime('%Y-%m-%d %H:%M:%S')},
    'date_end': {'string': u'Fecha Final', 'type': 'datetime',
        'default': time.strftime('%Y-%m-%d 23:59:59')},
    #'date_end': {'string': u'Fecha Final', 'type': 'datetime', 'default': time.strftime('%Y-%m-%d 23:59:59')},
    'invoice_ids': {'string': u'Facturas', 'type': 'many2many',
        'relation': 'account.invoice', 'domain': "[('type', 'in', \
        ['out_invoice', 'out_refund'] )]"}
}


def _create_facturae_txt(self, cr, uid, data, context=None):
    if context is None:
        context = {}
    pool = pooler.get_pool(cr.dbname)
    invoice_obj = pool.get('account.invoice')
    invoice_ids = data['form']['invoice_ids'][0][2]
    if invoice_ids:
        txt_data, fname = invoice_obj._get_facturae_invoice_txt_data(
            cr, uid, invoice_ids, context=context)
        if txt_data:
            txt_data = base64.encodestring(txt_data)
            return {'facturae': txt_data, 'facturae_fname': fname,
                'note': _('Abra el archivo y verfique que la informacion, \
                este correcta. Folios, RFC, montos y estatus reportados.\nAsegurese \
                de que no este reportando folios, que no pertenecen a facturas \
                electronicas (se pueden eliminar directamente en el archivo)\
                .\nTIP: Recuerde que este archivo tambien contiene folios de \
                nota de credito.')}
    return {}

end_form = """<?xml version="1.0"?>
<form string="ARCHIVO TXT PARA EL SAT">
    <newline/>
    <separator/>
    <newline/>
    <field name="facturae" filename="facturae_fname" nolabel="1"/>
    <field name="facturae_fname" invisible="1"/>
    <newline/>
    <separator string="IMPORTANTE"/>
    <newline/>
    <group  rowspan="10" colspan="4">
        <field name="note" readonly="1" nolabel="1"/>
    </group>
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


def _get_invoices_month(self, cr, uid, data, context=None):
    if context is None:
        context = {}
    pool = pooler.get_pool(cr.dbname)
    invoice_obj = pool.get('account.invoice')

    invoice_ids = data['form']['invoice_ids'][0][2]

    year = data['form']['year']
    month = data['form']['month']
    date_start = datetime.datetime(year, month, 1, 0, 0, 0)
    date_end = date_start + relativedelta(months=1)
    context.update({'date': date_start.strftime("%Y-%m-%d")})
    invoice_ids.extend(
        invoice_obj.search(cr, uid, [
            ('type', 'in', ['out_invoice', 'out_refund']),
            ('state', 'in', ['open', 'paid', 'cancel']),
            ('invoice_datetime', '>=', date_start.strftime(
                "%Y-%m-%d %H:%M:%S")),
            ('invoice_datetime', '<', date_end.strftime("%Y-%m-%d %H:%M:%S")),
            ('number', '<>', False),
        ], order='invoice_datetime', context=context)
    )

    invoice_ids.extend(
        invoice_obj.search(cr, uid, [
            ('type', 'in', ['out_invoice', 'out_refund']),
            ('state', 'in', ['cancel']),
            ('date_invoice_cancel', '>=', date_start.strftime(
                "%Y-%m-%d %H:%M:%S")),
            ('date_invoice_cancel', '<', date_end.strftime(
                "%Y-%m-%d %H:%M:%S")),
            ('number', '<>', False),
        ], order='invoice_datetime', context=context)
    )
    invoice_ids = list(set(invoice_ids))
    return {'invoice_ids': invoice_ids}


def _get_invoices_date(self, cr, uid, data, context=None):
    # invoice_ids.append(19)
    if context is None:
        context = {}
    pool = pooler.get_pool(cr.dbname)
    invoice_obj = pool.get('account.invoice')

    invoice_ids = data['form']['invoice_ids'][0][2]

    date_start = data['form']['date_start']
    date_end = data['form']['date_end']

    # context.update( {'date': date_start.strftime("%Y-%m-%d")} )

    invoice_ids.extend(
        invoice_obj.search(cr, uid, [
            ('type', 'in', ['out_invoice', 'out_refund']),
            ('state', 'in', ['open', 'paid', 'cancel']),
            ('invoice_datetime', '>=', date_start),
            ('invoice_datetime', '<', date_end),
            ('internal_number', '<>', False),
        ], order='invoice_datetime', context=context)
    )
    invoice_ids.extend(
        invoice_obj.search(cr, uid, [
            ('type', 'in', ['out_invoice', 'out_refund']),
            ('state', 'in', ['cancel']),
            ('date_invoice_cancel', '>=', date_start),
            ('date_invoice_cancel', '<', date_end),
            ('internal_number', '<>', False),
        ], order='invoice_datetime', context=context)
    )
    return {'invoice_ids': invoice_ids}


class wizard_invoice_facturae_txt(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form',
                       'arch': _form,
                       'fields': _fields,
                       'state': [('end', '_Cancel'), ('get_invoices_date',
                            'Obtener Facturas por filtro de _Fechas'), (
                            'get_invoices_month', 'Obtener Facturas por filtro \
                            de _Mes'), ('export', '_Generar Reporte Mensual TXT',
                            'gtk-ok', 'True')]}
        },

        'export': {
            'actions': [_create_facturae_txt],
            'result': {'type': 'form',
                       'arch': end_form,
                       'fields': end_fields,
                       'state': [('end', 'Ok', 'gtk-ok')]}
        },

        'get_invoices_month': {
            'actions': [_get_invoices_month],
            'result': {'type': 'state', 'state': 'init'},
        },

        'get_invoices_date': {
            'actions': [_get_invoices_date],
            'result': {'type': 'state', 'state': 'init'},
        }

    }
wizard_invoice_facturae_txt('wizard.invoice.facturae.txt')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
