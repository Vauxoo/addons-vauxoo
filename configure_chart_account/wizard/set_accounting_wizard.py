# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Jorge Angel Naranjo(jorge_nr@vauxoo.com)
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


class SetAccountingDataWizard(osv.osv_memory):
    _name = 'set.accounting.data.wizard'

    _columns = {
        'account_ids': fields.many2many('account.account',
                                        'account_account_partner_rel', 'parent_id', 'account_id',
                                        'Account'),
        'parent_id': fields.many2one('account.account', 'Parent',
                                     help='This account will be assigned as parent for '
                                     'the accounts selects in the previous field.',
                                     ondelete='cascade', domain=[('type', '=', 'view')]),
        'account_analytic_ids': fields.many2many('account.analytic.account',
                                                 'account__analytic_account_partner_rel', 'parent_id', 'account_id',
                                                 'Account'),
        'parent_analytic_id': fields.many2one('account.analytic.account',
                                              'Parent', help='This account will be assigned as parent for '
                                              'the analytic accounts selects in the previous field.',
                                              ondelete='cascade', domain=[('type', '=', 'view')]),
        'type_accounts': fields.selection([('accounts', 'Accounts'),
                                           ('analytic_accounts', 'Analytic Accounts')], 'Type Accounts',
                                          required=True),
    }

    _defaults = {
        'type_accounts': 'accounts'
    }

    def set_accounting_company(self, cr, uid, ids, context=None):
        """This wizard assigns a partner account and change your account
        type to root/view .
        """
        data = self.browse(cr, uid, ids, context=context)[0]
        if data.type_accounts == 'accounts':
            cr.execute("""
                UPDATE account_account SET type='view' WHERE id IN
                (SELECT DISTINCT id
                    FROM account_account WHERE type <> 'view' AND id IN
                        (SELECT DISTINCT parent_id FROM account_account
                            WHERE parent_id IS NOT NULL))""")
            for acc in data.account_ids:
                if acc.id != data.parent_id.id:
                    self.pool.get('account.account').write(cr, uid, [acc.id],
                                                           {'parent_id': data.parent_id.id})

        if data.type_accounts == 'analytic_accounts':
            for acc in data.account_analytic_ids:
                if acc != data.parent_analytic_id.id:
                    self.pool.get('account.analytic.account').write(cr, uid,
                                                                    [acc.id], {'parent_id': data.parent_analytic_id.id})
        return True
