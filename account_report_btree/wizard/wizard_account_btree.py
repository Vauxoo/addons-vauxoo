# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
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
import pooler
import time
import datetime

from mx.DateTime import *


dates_form = '''<?xml version="1.0"?>
<form string="Reporte de Auxiliares">
    <field name="date_ini" colspan="4"/>
    <field name="date_fin" colspan="4"/>
    <field name="nivel" colspan="4"/>
    <field name="account_ids" colspan="4"/>
</form>'''

dates_fields = {
    'date_ini': {'string': 'Fecha Inicial', 'type': 'date', 'required': True},
    'date_fin': {'string': 'Fecha Final', 'type': 'date', 'required': True},
    'nivel': {'string': 'Nivel', 'type': 'integer', 'required': True},
    'account_ids': {'string': 'Cuentas', 'type': 'many2many', 'relation': 'account.account'}
}

class reportes_btree_wizard(wizard.interface):
	states = {
		'init': {
			'actions': [],
			'result': {'type':'form', 'arch':dates_form, 'fields':dates_fields, 'state':[('end','Cancelar'),('report','Imprimir')]}
		},
		'report': {
			'actions': [],
			'result': {'type':'print', 'report':'reportes.btree.report', 'state':'end'}
		}
	}
reportes_btree_wizard('reportes.btree.wizard')

