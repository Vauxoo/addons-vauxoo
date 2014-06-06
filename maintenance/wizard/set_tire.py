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

_arch = UpdateableStr()
_fields = UpdateableDict()

def _get_form(self, cr, uid, data, ctx):
    _fields.clear()
    _arch_lst = ['<?xml version="1.0"?>', '<form string="Llantas">']
    for tracto in pooler.get_pool(cr.dbname).get('product.product').browse(cr, uid, [data['id']]):
        if tracto.axle_type != 'caja4' and tracto.axle_type != 'caja8':
            _arch_lst += ['<separator string="EJE Delantero" colspan="4"/>','<field name="front_left"/>', '<field name="front_right"/>']
            _fields['front_left'] = {'string':'Izquierdo', 'type':'many2one', 'relation':'product.product', 'required':True, 'default':tracto.front_left and tracto.front_left.id or False}
            _fields['front_right'] = {'string':'Derecho', 'type':'many2one', 'relation':'product.product', 'required':True, 'default':tracto.front_right and tracto.front_right.id or False}
        
        _arch_lst += ['<separator string="EJE Trasero" colspan="4"/>','<group colspan="4" col="8">','<field name="rear_left2"/>','<field name="rear_left"/>','<field name="rear_right"/>','<field name="rear_right2"/>', '</group>']
        _fields['rear_left'] = {'string':'Izquierdo', 'type':'many2one', 'relation':'product.product', 'required':True, 'default':tracto.rear_left and tracto.rear_left.id or False}
        _fields['rear_left2'] = {'string':'Izquierdo 2', 'type':'many2one', 'relation':'product.product', 'required':True, 'default':tracto.rear_left2 and tracto.rear_left2.id or False}
        _fields['rear_right'] = {'string':'Derecho', 'type':'many2one', 'relation':'product.product', 'required':True, 'default':tracto.rear_right and tracto.rear_right.id or False}
        _fields['rear_right2'] = {'string':'Derecho 2', 'type':'many2one', 'relation':'product.product', 'required':True, 'default':tracto.rear_right2 and tracto.rear_right2.id or False}
            
        if tracto.axle_type != 'tracto6' and tracto.axle_type != 'caja4':
            _arch_lst += ['<separator string="EJE Trasero 2" colspan="4"/>','<group colspan="4" col="8">','<field name="rear2_left2"/>','<field name="rear2_left"/>','<field name="rear2_right"/>','<field name="rear2_right2"/>', '</group>']
            _fields['rear2_left'] = {'string':'Izquierdo', 'type':'many2one', 'relation':'product.product', 'required':True, 'default':tracto.rear2_left and tracto.rear2_left.id or False}
            _fields['rear2_left2'] = {'string':'Izquierdo 2', 'type':'many2one', 'relation':'product.product', 'required':True, 'default':tracto.rear2_left2 and tracto.rear2_left2.id or False}
            _fields['rear2_right'] = {'string':'Derecho', 'type':'many2one', 'relation':'product.product', 'required':True, 'default':tracto.rear2_right2 and tracto.rear2_right2.id or False}
            _fields['rear2_right2'] = {'string':'Derecho 2', 'type':'many2one', 'relation':'product.product', 'required':True, 'default':tracto.rear2_right2 and tracto.rear2_right2.id or False}
            
    _arch_lst += ['<separator string="Refacciones" colspan="4"/>', '<field name="refaccion1"/>', '<field name="refaccion2"/>']
    _fields['refaccion1'] = {'string':'Refaccion 1', 'type':'many2one', 'relation':'product.product', 'default':tracto.refaccion1 and tracto.refaccion1.id or False}
    _fields['refaccion2'] = {'string':'Refaccion 2', 'type':'many2one', 'relation':'product.product', 'default':tracto.refaccion2 and tracto.refaccion2.id or False}
    _arch_lst.append('</form>')
    _arch.string = '\n'.join(_arch_lst)
    return {}

def _set(self, cr, uid, data, context):
    product_obj = pooler.get_pool(cr.dbname).get('product.product')
    hist_obj = pooler.get_pool(cr.dbname).get('tire.history')
    for tracto in product_obj.browse(cr, uid, [data['id']]):
        for key in data['form'].iterkeys():
            value = eval('tracto.%s.id'%key)
            if value != data['form'][key]:
                tire = product_obj.browse(cr, uid, [data['form'][key]])[0]
                product_obj.write(cr, uid, tracto.id, {key:data['form'][key]} )
                hist_obj.create(cr, uid, {
                        'tracto_id': tracto.id,
                        'tire_id': data['form'][key],
                        'distance': tire.recorrido,
                        'position': key,})
    return {}

class set(wizard.interface):

    states = {
        'init': {
            'actions': [ _get_form ],
            'result': {'type': 'form', 'arch': _arch, 'fields': _fields,
                'state' : (
                    ('end', 'Cancel'),
                    ('set', 'Cambiar')
                )
            },
        },
        'set': {
            'actions': [],
            'result': {
                'type': 'action',
                'action': _set,
                'state': 'end',
            },
            }
    }

set('wizard.set.tire')
