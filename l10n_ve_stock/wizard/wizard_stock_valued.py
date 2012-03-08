# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Netquatro C.A. (http://openerp.netquatro.com/) All Rights Reserved.
#                    Javier Duran <javier.duran@netquatro.com>
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import wizard
import osv
import pooler
from tools.translate import _
from tools.misc import UpdateableStr, UpdateableDict


_start_form = '''<?xml version="1.0"?>
<form string=" Generacion del Nro de la Nota de Entrega">   
    <separator string="Esta seguro de generar una Nota de entrega ?, este es un documento legal que deberá ser impreso en forma libre." colspan="4"/>
    <field name="type"/>
    <newline/>
    <field name="sure"/>
    <image name="gtk-dialog-info" colspan="2"/>
    <label string="Este proceso generara el correlativo automaticamente para el numero de la nota de entrega" colspan="2"/>
</form>'''

_start_fields = {
    'type':{
        'string':"Tipo",
        'type':'selection',
        'selection':[('entrega','Nota de Entrega (Con Precios)'),('despacho','Nota de Entrega (Sin Precios)')],
        'default': lambda *a:'entrega'
    },    
    'sure': {'string':'Esta Seguro?', 'type':'boolean'},
   
}

_transaction_form = '''<?xml version="1.0"?>
<form string=" Generacion del Nro de la Nota de Entrega">   
    <separator string="Esta seguro de generarlo ?" colspan="4"/>
    <field name="note"/>
    <newline/>
    <field name="sure2"/>
</form>'''
#_moves_arch = UpdateableStr()
_transaction_fields = UpdateableDict()
_note_form = '''<?xml version="1.0"?>
<form string=" VERIFICAR NOTA DE ENTREGA">   
    <separator string="NOTA DE ENTREGA CON NOTA ?" colspan="4"/>
    <field name="note2"/>
    <newline/>
    <field name="sure3"/>
</form>'''

_note_fields = UpdateableDict()

_reason_form = '''<?xml version="1.0"?>
<form string=" Razon de la nota de entrega sin valor">   
    <separator string="Elija un motivo por el cual genera una Nota de Entrega Sin Precios?" colspan="4"/>
    <field name="reason"/>
    <newline/>
    <field name="sure4"/>
</form>'''

_reason_fields = {
    'reason':{
        'string':"Motivo",
        'type':'selection',
        'selection':[('rep','Reparación'),('tdep','Traslado a depósito'),
                    ('talmo','Traslado almacenes o bodegas de otros'),('talmp','Traslado almacenes o bodegas propios'),
                    ('tdis','Traslado para su distribución'),('otr','Otros')],
        'default': lambda *a:'talmp'
    },    
    'sure4': {'string':'Esta Seguro?', 'type':'boolean'},
   
}



_end_form = '''<?xml version="1.0"?>
<form string="Correlativo Generado">
    <label string="El numero de la orden fue creado con exito !" colspan="4"/>
    <field name="nro" colspan="4" nolabel="1"/>
</form>'''
_end_fields = UpdateableDict()


def make_default(val):
    def fct(uid, data, state):
        return val
    return fct


def make_nro(cr, uid, ids, context):
    pool = pooler.get_pool(cr.dbname)
    cr.execute('SELECT id, number ' \
            'FROM stock_picking ' \
            'WHERE id IN ('+','.join(map(str,ids))+')')

    for (id, number) in cr.fetchall():
        if not number:
            number = pool.get('ir.sequence').get(cr, uid, 'stock.valued')
        cr.execute('UPDATE stock_picking SET number=%s ' \
                'WHERE id=%s', (number, id))

    return number


def _get_type(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    pick_obj = pool.get('stock.picking')
    id = data['id']

    pick = pick_obj.browse(cr, uid, id)
    if pick.type != 'out':
        raise wizard.except_wizard(_('Error Usuario'), _('No puede generar correlativo, para este tipo de nota\nTipo: %s') % (pick.type))

    return {}

def _get_note(self, cr, uid, data, context):
    if not data['form']['sure']:
        raise wizard.except_wizard(_('Error Usuario'), _('Generar Correlativo, !Por Favor seleccione la opcion!'))
    pool = pooler.get_pool(cr.dbname)
    pick_obj = pool.get('stock.picking')
    id = data['id']
    _transaction_fields.clear()
    req = True

    pick = pick_obj.browse(cr, uid, id)

    if data['form']['type']=='entrega':
        req = False

    _transaction_fields['note'] = {'string':'Nota', 'type':'char', 'default' : make_default(pick.note),'required':req}
    _transaction_fields['sure2'] = {'string':'Esta de Acuerdo?', 'type':'boolean', 'default': lambda *a: False}


    return {}


def _check_agree(self, cr, uid, data, context):
    if not data['form']['sure2']:
        raise wizard.except_wizard(_('Error Usuario'), _('Por favor revise la nota y si es correcta seleccione la opcion de estar de acuerdo!'))


    return {}


def _rev_note(self, cr, uid, data, context):
    _note_fields.clear()
    
    _note_fields['note2'] = {'string':'Nota', 'type':'char', 'default' : make_default(data['form']['note'])}
    _note_fields['sure3'] = {'string':'Esta de Acuerdo?', 'type':'boolean', 'default': lambda *a: False}


    return {}


def _get_reason(self, cr, uid, data, context):
#    _reason_fields.clear()
    
#    _reason_fields['note2'] = {'string':'Nota', 'type':'char', 'default' : make_default(data['form']['note'])}
#    _reason_fields['sure4'] = {'string':'Esta de Acuerdo?', 'type':'boolean', 'default': lambda *a: False}


    return {}


def _data_save(self, cr, uid, data, context):
    agree = data['form'].get('sure3',data['form']['sure2'])
    comment = data['form'].get('note2',data['form']['note'])
    razon = data['form'].get('reason',False)
    motiv = {
            'rep':'Reparación',
            'tdep':'Traslado a depósito',
            'talmo':'Traslado almacenes o bodegas de otros',
            'talmp':'Traslado almacenes o bodegas propios',
            'tdis':'Traslado para su distribución',
            'otr':'Otros'            
    }

    if not agree:
        raise wizard.except_wizard(_('Error Usuario'), _('Por favor revise la nota y si es correcta seleccione la opcion de estar de acuerdo!'))

    pool = pooler.get_pool(cr.dbname)
    pick_obj = pool.get('stock.picking')
    id = data['id']
    _end_fields.clear()

    pick = pick_obj.browse(cr, uid, id)

    if pick.type == 'out':
        number = make_nro(cr, uid, [id], context)
        if razon:
            comment += '\n' + motiv[razon]
        pick_obj.write(cr, uid, [id], {'note': comment})
        _end_fields['nro'] = {'string':'Numero' ,'type':'char', 'size': 32, 'readonly':True, 'default' : make_default(number)}


    return {}




class wiz_nota_entrega(wizard.interface):

    def _check(self, cr, uid, data, context):
        if data['form']['type']=='despacho':
            return 'guia_note'
        if data['form']['type']=='entrega' and data['form']['note']:
            return 'val_note'
        else:
            return 'shownro'

    def _check_rep(self, cr, uid, data, context):
        if data['form']['type']=='entrega':
            return 'printval'
        else:
            return 'printdesp'


    states = {
        'init': {
            'actions': [_get_type],
            'result': {'type': 'form', 'arch':_start_form, 'fields':_start_fields, 'state':[('end','Cancel'),('get_data','Continuar')]}
        },
        'get_data': {
            'actions': [_get_note],
            'result': {'type': 'form', 'arch': _transaction_form, 'fields': _transaction_fields, 'state' : [
                    ('end', 'Cancel'),
                    ('checknote', 'Continuar')
                ]
            }

        },
        'checknote': {
            'actions': [_check_agree],
            'result': {'type':'choice','next_state':_check}

        },
        'val_note': {
            'actions': [_rev_note],
            'result': {'type': 'form', 'arch': _note_form, 'fields': _note_fields, 'state' : [
                    ('end', 'Cancel'),
                    ('shownro', 'Aceptar')
                ]
            }

        },
        'guia_note': {
            'actions': [],
            'result': {'type': 'form', 'arch': _reason_form, 'fields': _reason_fields, 'state' : [
                    ('end', 'Cancel'),
                    ('shownro', 'Aceptar')
                ]
            }

        },
        'shownro': {
            'actions': [_data_save],
            'result': {'type': 'form', 'arch': _end_form, 'fields': _end_fields, 'state' : [
                    ('end', 'Cancel'),
                    ('checkreport', 'Imprimir','gtk-print')
                ]
            }

        },
        'checkreport': {
            'actions': [],
            'result': {'type':'choice','next_state':_check_rep}

        },
        'printval': {
            'actions': [],
            'result': {'type':'print', 'report':'stock.valued_ve', 'state':'end'}

        },
        'printdesp': {
            'actions': [],
            'result': {'type':'print', 'report':'stock.guia_ve', 'state':'end'}

        }


    }
wiz_nota_entrega('stock_valued_nro')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

