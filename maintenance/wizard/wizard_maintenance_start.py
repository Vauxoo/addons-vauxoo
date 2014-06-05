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
<form string="Mantenimientos Pendientes">
	<separator string="Indique la Fecha de Terminacion del Mantenimiento" colspan="4"/>
	<field name="date"/>
</form>'''
_fields = {
		'date': {'type':'datetime', 'required':True, 'string':'Fecha Termino'},
	}

def _set_date(self, cr, uid, data, context):
	mol_obj = pooler.get_pool(cr.dbname).get('maintenance.order.line')
	for mol in mol_obj.browse(cr, uid, data['ids']):
		mol_obj.write(cr, uid, mol.id, {'date_release':data['form']['date'], 'state':'in_progress'})
	return {}


class maintenance_start(wizard.interface):
	states = {
		'init': {
				'actions': [],
				'result': {'type':'form', 'arch':_arch, 'fields':_fields,
					'state': (
							('set_date','_Comenzar'),
							('end', '_Salir'),
						)
				}
			},

		'set_date': {
				'actions': [],
				'result': {
						'type': 'action',
						'action': _set_date,
						'state': 'end'
					},
			},
	}

maintenance_start('wizard.maintenance.start')
