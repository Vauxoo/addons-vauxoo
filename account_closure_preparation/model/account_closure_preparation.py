#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://www.vauxoo.com>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Humberto Arocha <humbertoarocha@gmail.com>
#    Planified by: Moises Lopez <moylop260@gmail.com>
#    Audited by: Nhomar Hernandez <nhomar@gmail.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp.osv import osv, fields

class account_closure_preparation(osv.TransientModel):

    '''Prepare a Chart of Account to be used properly when closing a
    fiscayear'''

    _name = 'account.closure.preparation'

    _columns = {
        'company_id':fields.many2one('res.company', 'Company', required=True,
            help=('Company to which the chart of account is going to be'
            ' prepared')),
        'root_id':fields.many2one('account.account', 'Root Account',
            domain="[('company_id','=',company_id),('type','=','view'),('parent_id','=',None)]",
            required=True, help=('Root Account, the account that plays as a'
                'Chart of Accounts')),
        'view_ut_id':fields.many2one('account.account.type', 'Closure Type',
            required=True, domain="[('close_method','=','none')]",
            help=('Select the Account Type that will be used when fixing your'
            ' chart of account')), 
        'bs_ids':fields.many2many('account.account', 'acp_bs_acc_rel',
            'account_id', 'acp_id', 'Balance Sheet Accounts',
            domain="[('parent_id','=',root_id)]", help=('Balance Sheet '
                'Accounts, Just Select the most top level in the chart of '
                'account related to the Balance Sheet')),
        'bs_ut_id':fields.many2one('account.account.type', 'BS Closure Type',
            required=True, domain="[('close_method','=','balance')]",
            help=('Select the Account Type that will be used when fixing your '
            'chart of account')), 
        'is_ids':fields.many2many('account.account', 'acp_is_acc_rel',
            'account_id', 'acp_id', 'Income Statement Accounts',
            domain="[('parent_id','=',root_id)]", help=('Balance Sheet '
                'Accounts, Just Select the most top level in the chart of '
                'account related to the Balance Sheet')),
        'is_ut_id':fields.many2one('account.account.type', 'IS Closure Type',
            required=True, domain="[('close_method','=','none')]",
            help=('Select the Account Type that will be used when fixing your '
            'chart of account')), 
        'state':fields.selection([
            ('draft','Readying Chart of Account'),
            ('stage2','Preping BS Accounts'),
            ('stage3','Preping IS Accounts'),
            ], help='State'), 
            }

    _defaults = {
        'state': 'draft',
        'company_id': lambda s, c, u, ctx: \
            s.pool.get('res.users').browse(c, u, u, context=ctx).company_id.id,
        }
    def prepare_chart(self, cr, uid, ids, context=None):
        context = context or {}
        wzr_brw = self.browse(cr,uid,ids[0],context=context)
        wzr_brw.write({'state':'stage2'})
        return {}
    
