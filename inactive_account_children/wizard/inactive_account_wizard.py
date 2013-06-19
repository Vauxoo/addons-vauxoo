# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Ernesto García (ernesto_gm@vauxoo.com)
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


class inactive_account_wizard(osv.osv_memory):
	_name = 'inactive.account.wizard'
	
	def get_accounts(self, cr, uid, ids, context=None):
		data = self.read(cr, uid, ids)[0]
		account_ids = data['account_ids']
		for account in account_ids:
			cr.execute("""SELECT node.company_id,node.type,node.id as id,node.name
				FROM account_account AS node,account_account AS parent
				WHERE node.parent_left BETWEEN parent.parent_left
				AND parent.parent_right
				AND parent.id = %s
				ORDER BY parent.parent_left""", (account,))
			res = cr.dictfetchall()
			for account_children in res:
				self.pool.get('account.account').write(cr, uid,
					account_children['id'], {'active' : False})
			
	_columns = {
		'account_ids' : fields.many2many('account.account',
                                         'account_account_rel',
                                         'account_wizard_id',
                                         'account_id', 'accounts'),
	}
