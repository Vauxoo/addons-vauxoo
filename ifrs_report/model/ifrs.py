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
	'ifrs_lines_ids' : fields.one2many('ifrs.lines', 'ifrs_id', 'IFRS lines' ), # requiered? #  //parent left and parent right...
	'state': fields.selection( [
		('draft','Draft'),
		('ready', 'Ready'),
		('done','Done'),
		('cancel','Cancel') ],
		'State', required=True )
	}

	_defaults = {
		'state' : 'draft',
	}

ifrs_ifrs()

class ifrs_lines(osv.osv):

	_name = 'ifrs.lines'
	_columns = {
	'sequence' : fields.integer( 'Sequence', required = True ), # HAY QUE HACER ALGO ADEMAS?
	'name' : fields.char( 'Name', 128, required = True ),
	'ifrs_id' : fields.many2one('ifrs.ifrs', 'IFRS' ), # required= True

	'cons_ids' : fields.many2many('account.account', 'ifrs_account_rel', 'ifrs_lines_id', 'account_id', string='Consolidated Accounts' ),



	# amount : campo funcional, tipo float
	# type, selecctionm abstract, REQUIRED = true
		# abstract -> solo nombre
		# detail -> con datos
		# total -> totalizador...
	# total_ids, m2m, para hacer totalizaciones, que se relaciona con la misma clase... y que es funcional al mismo tiepo, porque es la suma # many2many(obj, rel, field1, field2, ...)
	}

ifrs_lines()
