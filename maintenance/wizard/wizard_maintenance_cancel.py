# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Julio Serna(julio@vauxoo.com)
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

import time
import netsvc
from tools.misc import UpdateableStr, UpdateableDict
import pooler

import wizard
from osv import osv

_arch = '''<?xml version="1.0"?>
<form string="Mantenimientos">
    <separator string="Desea Cancelar o Reasignar el Mantenimiento" colspan="4"/>
</form>'''
_fields = {
    }

_arch2 = '''<?xml version="1.0"?>
<form string="Mantenimientos Pendientes">
    <separator string="Asigne una Fecha Compromiso" colspan="4"/>
    <field name="date"/>
</form>'''
_fields2 = {
        'date': {'type':'date', 'required':True, 'string':'Fecha Compromiso'},
    }

def _check(self, cr, uid, data, context):
    for maintenance in pooler.get_pool(cr.dbname).get('maintenance.order').browse(cr, uid, data['ids']):
        for line in maintenance.line_ids:
            if line.state == 'draft':
                return 'confirm'
        pooler.get_pool(cr.dbname).get('maintenance.order').write(cr, uid, data['ids'], {'state':'done'})
    return 'end'

def _cancel(self, cr, uid, data, ctx):
    mol_obj = pooler.get_pool(cr.dbname).get('maintenance.order.line').write(cr, uid, data['id'], {'state':'cancel'})
    return  {}

def _reassign(self, cr, uid, data, context):
    mol_obj = pooler.get_pool(cr.dbname).get('maintenance.order.line')
    for mol in mol_obj.browse(cr, uid, data['ids']):
        mol_id = mol_obj.copy(cr, uid, mol.id, {'date_due':data['form']['date'], 'picking_ids':[], 'pendiente_id':mol.id})
        mol_obj.write(cr, uid, mol.id, {'state':'reassigned'})
    return {
        'domain': "[('id','in', [" + str(mol_id) + "])]",
        'name': 'Mantenimientos',
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'maintenance.order.line',
        'view_id': False,
        'type': 'ir.actions.act_window'
    }


class maintenance_cancel(wizard.interface):
    states = {
        'init': {
            'actions': [ ],
            'result': {'type': 'form', 'arch': _arch, 'fields': _fields,
                'state' : (
                    ('get_date', '_Reasignar'),
                    ('cancelar', '_Cancelar'),
                    ('end', '_Salir')
                )
            },
        },
        
        'get_date': {
                'actions': [],
                'result': {'type':'form', 'arch':_arch2, 'fields':_fields2,
                    'state': (
                            ('reassign','_Reasignar'),
                            ('end', '_Salir'),
                        )
                }
            },
            
        'reassign': {
                'actions': [],
                'result': {
                        'type': 'action',
                        'action': _reassign,
                        'state': 'end'
                    },
            },
        
        'cancelar': {
            'actions': [],
            'result': {
                'type': 'action',
                'action': _cancel,
                'state':'end',
            },
        },
    }

maintenance_cancel('wizard.maintenance.cancel')
