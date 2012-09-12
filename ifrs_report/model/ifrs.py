#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Katherine Zaoral <katherine.zaoral@vauxoo.com>
#    Coded by: Yanina Aular <yanina.aular@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

from osv import osv
from osv import fields

class ifrs_ifrs(osv.osv):

	_name = 'ifrs.ifrs'
	_columns = {
	'name' : fields.char('Name', 128, required = True ),
	'company_id' : fields.many2one('res.company', string='Company', ondelete='cascade', required = True ),
	'title' : fields.text('Title', required = True ),
	'ifrs_lines_ids' : fields.one2many('ifrs.lines', 'ifrs_id', 'IFRS lines' ),
	### NOTAK; PREGUNTA ¿necesita campo required?
	### NOTAK; HACER parent left and aprent right...

	'state': fields.selection( [
		('draft','Draft'),
		('ready', 'Ready'),
		('done','Done'),
		('cancel','Cancel') ],
		'State', required=True )

	### NOTAK; HACER agregar campo año fiscal, modelo = account.fiscal.year / probar
	#'fiscal_year' : fields.one2many('account.fiscalyear', 'fiscalyear_id', 'Fiscal Year' ),
	}

	_defaults = {
		'state' : 'draft',
	}

ifrs_ifrs()

class ifrs_lines(osv.osv):

	_name = 'ifrs.lines'

	#~ Calcular suma
	def _get_sum( self, cr, uid, id, context = None ):
		if context is None: context = {}
		res = 0
		brw = self.browse( cr, uid, id, context = context )

		if brw.type == 'abtract':
			pass
		elif brw.type == 'detail':
			for a in brw.cons_ids:
				res += a.balance
		elif brw.type == 'total':
			for c in brw.total_ids:
				res += self._get_sum( cr, uid, c.id, context = context )
		return res

	#~ Generalidad para calcular totales..
	def _consolidated_accounts_sum( self, cr, uid, ids, field_name, arg, context = None ):
		if context is None: context = {}
		res = {}
		for id in ids:
			res[id] = self._get_sum( cr, uid, id, context = context )
		return res

	### NOTAK; HACER probar si se muere con el tipo de ifrs TOTAL

	_columns = {
	'sequence' : fields.integer( 'Sequence', required = True ),
	### NOTAK; PREGUNTAR ¿Hay que hacer algo mas?

	'name' : fields.char( 'Name', 128, required = True ),
	'ifrs_id' : fields.many2one('ifrs.ifrs', 'IFRS' ),
	### NOTAK; PREGUNTAR required = True?

	'cons_ids' : fields.many2many('account.account', 'ifrs_account_rel', 'ifrs_lines_id', 'account_id', string='Consolidated Accounts' ),

	'type': fields.selection( [
		('abstract','Abstract'),
		('detail', 'Detail'),
		('total','Total') ] ,
		'Type', required = True ),

	#~ ''' TYPE: abstract solo muestra el nombre de la cuenta, Detail muestra las cantidades, Total es un totalizador, suma las cuentas que se le son indicadas '''

	'amount' : fields.function( _consolidated_accounts_sum, method = True, type='float', string='Amount'),
	#~ 'amount' : fields.float('Amount'),

	'total_ids' : fields.many2many('ifrs.lines', 'ifrs_ifrs_rel', 'ifk1_id', 'ifk2_id', string='Total'),
	}

	_defaults = {
		'type' : 'abstract',
	}

ifrs_lines()
