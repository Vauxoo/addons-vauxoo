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
	<separator string="Hay mantenimientos pendientes asigne una fecha compromiso" colspan="4"/>
	<field name="date"/>
</form>'''
_fields = {
		'date': {'type':'date', 'required':True, 'string':'Fecha Compromiso'},
	}

def _check(self, cr, uid, data, context):
	mol_ids = pooler.get_pool(cr.dbname).get('maintenance.order.line')._check_maintenance(cr, uid, data['ids'])
	if mol_ids:
		return {
			'domain': "[('id','in', [" + ','.join(map(str,mol_ids)) + "])]",
			'name': 'Mantenimientos',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'maintenance.order.line',
			'view_id': False,
			'type': 'ir.actions.act_window'
		}
	return 'end'

class maintenance(wizard.interface):
	states = {
		'init': {
			'actions': [],
			'result': {
				'type': 'action',
				'action': _check,
				'state': 'end',
			},
		},
	}

maintenance('wizard.check.maintenance')
