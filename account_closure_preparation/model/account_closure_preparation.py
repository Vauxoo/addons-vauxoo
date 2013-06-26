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
        'account_ids':fields.many2many('account.account', 'acp_all_acc_rel',
            'account_id', 'acp_id', 'Balance Sheet Accounts',
            domain="[('parent_id','=',root_id)]", help=('Balance Sheet '
                'Accounts, Just Select the most top level in the chart of '
                'account related to the Balance Sheet')),
        'bs_ids':fields.many2many('account.account', 'acp_bs_acc_rel',
            'account_id', 'acp_id', 'Balance Sheet Accounts',
            domain="[('parent_id','=',root_id)]", help=('Balance Sheet '
                'Accounts, Just Select the most top level in the chart of '
                'account related to the Balance Sheet')),
        'bs_ut_id':fields.many2one('account.account.type', 'BS Closure Type',
            required=False, domain="[('close_method','=','balance')]",
            help=('Select the Account Type that will be used when fixing your '
            'chart of account')), 
        'is_ids':fields.many2many('account.account', 'acp_is_acc_rel',
            'account_id', 'acp_id', 'Income Statement Accounts',
            domain="[('parent_id','=',root_id)]", help=('Balance Sheet '
                'Accounts, Just Select the most top level in the chart of '
                'account related to the Balance Sheet')),
        'is_ut_id':fields.many2one('account.account.type', 'IS Closure Type',
            required=False, domain="[('close_method','=','none')]",
            help=('Select the Account Type that will be used when fixing your '
            'chart of account')), 
        'bk_ids':fields.many2many('account.account', 'acp_bk_acc_rel',
            'account_id', 'acp_id', 'Bank & Cash Accounts',
            domain="[('type','=','view')]", help=('Select the most top '
            'level in the chart of account related to your Bank Accounts')),
        'bk_ut_id':fields.many2one('account.account.type', 'Bank Closure Type',
            required=False, domain="[('close_method','=','balance')]",
            help=('Select the Account Type that will be used when fixing your '
            'chart of account')), 
        'state':fields.selection([
            ('stage1','Prep Chart'),
            ('stage2','Fix Chart'),
            ('stage3','Prep BS'),
            ('stage4','Fix BS'),
            ('stage5','Prep IS'),
            ('stage6','Fix IS'),
            ('stage7','Prep Bank Acc'),
            ('stage8','Fix Bank Acc'),
            ('stage9','Fix not Bank Acc'),
            ('stage10','Nxt Stp 2 Def'),
            ], help='State'), 
            }

    _defaults = {
        'state': 'stage1',
        'company_id': lambda s, c, u, ctx: \
            s.pool.get('res.users').browse(c, u, u, context=ctx).company_id.id,
        }
    def prepare_chart(self, cr, uid, ids, context=None):
        context = context or {}
        wzd_brw = self.browse(cr,uid,ids[0],context=context)
        context['company_id'] = wzd_brw.company_id.id
        acc_obj = self.pool.get('account.account')
        if wzd_brw.state == 'stage1':
            view_ids = acc_obj._get_children_and_consol(cr, uid, wzd_brw.root_id.id, context=context)
            view_ids = acc_obj.search(cr, uid,[
                                        ('id','in',view_ids),
                                        ('type','=','view'),
                                        ('user_type.close_method','!=','none'),
                                        ],context=context)
            wzd_brw.write({'state':'stage2','account_ids':[(6,0,view_ids)]})
        elif wzd_brw.state == 'stage2':
            res = [i.id for i in wzd_brw.account_ids]
            acc_obj.write(cr,uid,res,
                          {'user_type':wzd_brw.view_ut_id.id},context=context)
            wzd_brw.write({'state':'stage3','account_ids':[(6,0,[])]})
        elif wzd_brw.state == 'stage3':
            view_ids = acc_obj._get_children_and_consol(
                    cr, uid, [i.id for i in wzd_brw.bs_ids], context=context)
            view_ids = acc_obj.search(cr, uid,[
                                        ('id','in',view_ids),
                                        ('type','!=','view'),
                                        ('user_type.close_method','=','none'),
                                        ],context=context)
            wzd_brw.write({'state':'stage4','account_ids':[(6,0,view_ids)]})
        elif wzd_brw.state == 'stage4':
            res = [i.id for i in wzd_brw.account_ids]
            acc_obj.write(cr,uid,res,
                          {'user_type':wzd_brw.bs_ut_id.id},context=context)
            wzd_brw.write({'state':'stage5','account_ids':[(6,0,[])]})
        elif wzd_brw.state == 'stage5':
            view_ids = acc_obj._get_children_and_consol(
                    cr, uid, [i.id for i in wzd_brw.is_ids], context=context)
            view_ids = acc_obj.search(cr, uid,[
                                        ('id','in',view_ids),
                                        ('type','!=','view'),
                                        '|',('type','not in',('other','closed')),
                                        ('user_type.close_method','!=','none'),
                                        ],context=context)
            wzd_brw.write({'state':'stage6','account_ids':[(6,0,view_ids)]})
        elif wzd_brw.state == 'stage6':
            res = [i.id for i in wzd_brw.account_ids]
            acc_obj.write(cr,uid,res,
                          {'user_type':wzd_brw.is_ut_id.id,
                           'type':'other'},context=context)
            wzd_brw.write({'state':'stage7','account_ids':[(6,0,[])]})
        elif wzd_brw.state == 'stage7':
            view_ids = acc_obj._get_children_and_consol(
                    cr, uid, [i.id for i in wzd_brw.bk_ids], context=context)
            view_ids = acc_obj.search(cr, uid,[
                                        ('id','in',view_ids),
                                        ('type','!=','view'),
                                        '|',('type','!=','liquidity'),
                                        ('user_type.close_method','!=','balance'),
                                        ],context=context)
            wzd_brw.write({'state':'stage8','account_ids':[(6,0,view_ids)]})
        elif wzd_brw.state == 'stage8':
            res = [i.id for i in wzd_brw.account_ids]
            acc_obj.write(cr,uid,res,{
                          'user_type' : wzd_brw.bk_ut_id.id,
                          'type' : 'liquidity',
                          },context=context)
            bank_ids1 = acc_obj._get_children_and_consol(
                    cr, uid, [i.id for i in wzd_brw.bk_ids], context=context)
            bank_ids1x = acc_obj.search(cr, uid,[
                                        ('id','in',bank_ids1),
                                        ('type','!=','view'),
                                        ],context=context)
            bank_ids2 = acc_obj._get_children_and_consol(
                    cr, uid, wzd_brw.root_id.id, context=context)
            bank_ids2 = acc_obj.search(cr, uid,[
                                        ('id','in',bank_ids2),
                                        ('id','not in',bank_ids1x),
                                        ('type','!=','view'),
                                        ('type','=','liquidity'),
                                        ],context=context)
            wzd_brw.write({'state':'stage9','account_ids':[(6,0,bank_ids2)]})
        elif wzd_brw.state == 'stage9':
            res = [i.id for i in wzd_brw.account_ids]
            acc_obj.write(cr,uid,res,
                          {'type':'other'},context=context)
            wzd_brw.write({'state':'stage10','account_ids':[(6,0,[])]})
        return {}
    
