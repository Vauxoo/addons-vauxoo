# coding: utf-8
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


class AccountClosurePreparation(osv.TransientModel):

    """Prepare a Chart of Account to be used properly when closing a
    fiscayear"""

    _name = 'account.closure.preparation'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=False,
                                      help=('Company to which the chart of account is going to be'
                                            ' prepared')),
        'root_id': fields.many2one('account.account', 'Root Account',
                                   domain="[('company_id','=',company_id),('type','=','view'),('parent_id','=',None)]",
                                   required=False, help=('Root Account, the account that plays as a'
                                                         'Chart of Accounts')),
        'view_ut_id': fields.many2one('account.account.type', 'Closure Type',
                                      required=False, domain="[('close_method','=','none')]",
                                      help=('Select the Account Type that will be used when fixing your'
                                            ' chart of account')),
        'account_ids': fields.many2many('account.account', 'acp_all_acc_rel',
                                        'account_id', 'acp_id', 'Balance Sheet Accounts',
                                        domain="[('parent_id','=',root_id)]"),
        'bs_ids': fields.many2many('account.account', 'acp_bs_acc_rel',
                                   'account_id', 'acp_id', 'Balance Sheet Accounts',
                                   domain="[('parent_id','=',root_id)]", help=('Balance Sheet '
                                                                               'Accounts, Just Select the most top level in the chart of '
                                                                               'account related to the Balance Sheet')),
        'bs_ut_id': fields.many2one('account.account.type', 'BS Closure Type',
                                    required=False, domain="[('close_method','=','balance')]",
                                    help=('Select the Account Type that will be used when fixing your '
                                          'chart of account')),
        'is_ids': fields.many2many('account.account', 'acp_is_acc_rel',
                                   'account_id', 'acp_id', 'Income Statement Accounts',
                                   domain="[('parent_id','=',root_id),('id','not in',bs_ids[0][2])]",
                                   help=('Balance Sheet Accounts, Just Select the most top level in '
                                         'the chart of account related to the Balance Sheet')),
        'is_ut_id': fields.many2one('account.account.type', 'IS Closure Type',
                                    required=False, domain="[('close_method','=','none')]",
                                    help=('Select the Account Type that will be used when fixing your '
                                          'chart of account')),
        'bk_ids': fields.many2many('account.account', 'acp_bk_acc_rel',
                                   'account_id', 'acp_id', 'Bank & Cash Accounts',
                                   domain=("[('type','=','view'),"
                                           "('parent_id','child_of',bs_ids[0][2])]"),
                                   help=('Select the most top '
                                         'level in the chart of account related to your Bank Accounts')),
        'bk_ut_id': fields.many2one('account.account.type', 'Bank Closure Type',
                                    required=False, domain="[('close_method','=','balance')]",
                                    help=('Select the Account Type that will be used when fixing your '
                                          'chart of account')),
        'rec_ids': fields.many2many('account.account', 'acp_rec_acc_rel',
                                    'account_id', 'acp_id', 'Receivable Accounts',
                                    domain=("[('type','=','view'),"
                                            "('parent_id','child_of',bs_ids[0][2])]"),
                                    help=('Select the most top '
                                          'level in the chart of account related to your Receivable Accounts')),
        'rec_ut_id': fields.many2one('account.account.type', 'Receivable  Closure Type',
                                     required=False, domain="[('close_method','=','unreconciled')]",
                                     help=('Select the Account Type that will be used when fixing your '
                                           'chart of account')),
        'pay_ids': fields.many2many('account.account', 'acp_pay_acc_rel',
                                    'account_id', 'acp_id', 'Payable Accounts',
                                    domain=("[('type','=','view'),"
                                            "('parent_id','child_of',bs_ids[0][2])]"),
                                    help=('Select the most top '
                                          'level in the chart of account related to your Payable Accounts')),
        'pay_ut_id': fields.many2one('account.account.type', 'Payable  Closure Type',
                                     required=False, domain="[('close_method','=','unreconciled')]",
                                     help=('Select the Account Type that will be used when fixing your '
                                           'chart of account')),
        'recon_ids': fields.many2many('account.account', 'acp_recon_acc_rel',
                                      'account_id', 'acp_id', 'Reconcilable Accounts',
                                      domain=("[('type','=','other'),"
                                              "('parent_id','child_of',bs_ids[0][2])]"),
                                      help=('Select the most top '
                                            'you will regard as Reconcilable. Remember this Accounts are'
                                            ' different than your Receivable & Payable Accounts')),
        'recon_ut_id': fields.many2one('account.account.type', 'Reconcilable Closure Type',
                                       required=False, domain="[('close_method','=','unreconciled')]",
                                       help=('Select the Account Type that will be used when fixing your '
                                             'chart of account')),
        'det_ids': fields.many2many('account.account', 'acp_det_acc_rel',
                                    'account_id', 'acp_id', 'Detail Accounts',
                                    domain=("[('type','=','other'),"
                                            "('parent_id','child_of',bs_ids[0][2])]"),
                                    help=('Select the most top '
                                          'you will regard as Detail. This kind of Account is weirdly '
                                          'used. Although is could be used in Depreciation Accounts')),
        'det_ut_id': fields.many2one('account.account.type', 'Detail Closure Type',
                                     required=False, domain="[('close_method','=','detail')]",
                                     help=('Select the Account Type that will be used when fixing your '
                                           'chart of account')),
        'cons_id': fields.many2one('account.account', 'Consolidation Account',
                                   domain=("["
                                           "('company_id','=',company_id),"
                                           "('type','=','consolidation'),"
                                           "('parent_id','child_of',bs_ids[0][2])]"),
                                   required=False, help=('Consolidation Account, the account that '
                                                         'plays as a the Consolidation of the Income Statement in Your '
                                                         'Chart of Accounts')),
        'cons_ids': fields.many2many('account.account', 'acp_cons_acc_rel',
                                     'account_id', 'acp_id', 'Detail Accounts', readonly=False,
                                     help=('Accounts to be used in the Consolidation Account')),
        'state': fields.selection([
            ('stage1', 'Prep Chart'),
            ('stage2', 'Fix Chart'),
            ('stage3', 'Prep BS'),
            ('stage4', 'Fix BS'),
            ('stage5', 'Prep IS'),
            ('stage6', 'Fix IS'),
            ('stage7', 'Prep Bank Acc'),
            ('stage8', 'Fix Bank Acc'),
            ('stage9', 'Fix not Bank Acc'),
            ('stage10', 'Prep Rec Acc'),
            ('stage11', 'Fix Rec Acc'),
            ('stage12', 'Fix not Rec Acc'),
            ('stage13', 'Prep Pay Acc'),
            ('stage14', 'Fix Pay Acc'),
            ('stage15', 'Fix not Pay Acc'),
            ('stage16', 'Prep Reconcile Acc'),
            ('stage17', 'Fix Reconcile Acc'),
            ('stage18', 'Prep Detail Acc'),
            ('stage19', 'Fix Detail Acc'),
            ('stage20', 'Prep & Fix Consolation Acc'),
            ('stage21', 'LAST STEP'),
        ], help='State'),
        'skip': fields.boolean('Skip This Step', help=('Some time it is Ok to '
                                                       'skip a step because that configuration is not used in your company'
                                                       )),
    }

    _defaults = {
        'state': 'stage1',
        'company_id': lambda s, c, u, ctx:
        s.pool.get('res.users').browse(c, u, u, context=ctx).company_id.id,
    }

    def to_start(self, cr, uid, ids, context=None):
        context = context or {}
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        context['company_id'] = wzd_brw.company_id.id
        wzd_brw.write({'state': 'stage1'})
        return {}

    def backpedal(self, cr, uid, ids, context=None):
        context = context or {}
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        context['company_id'] = wzd_brw.company_id.id
        wzd_brw.write({'account_ids': [(6, 0, [])]})
        if wzd_brw.state == 'stage2':
            wzd_brw.write({'state': 'stage1'})
        elif wzd_brw.state == 'stage3':
            wzd_brw.write({'state': 'stage2'})
        elif wzd_brw.state == 'stage4':
            wzd_brw.write({'state': 'stage3'})
        elif wzd_brw.state == 'stage5':
            wzd_brw.write({'state': 'stage4'})
        elif wzd_brw.state == 'stage6':
            wzd_brw.write({'state': 'stage5'})
        elif wzd_brw.state == 'stage7':
            wzd_brw.write({'state': 'stage6'})
        elif wzd_brw.state == 'stage8':
            wzd_brw.write({'state': 'stage7'})
        elif wzd_brw.state == 'stage9':
            wzd_brw.write({'state': 'stage8'})
        elif wzd_brw.state == 'stage10':
            wzd_brw.write({'state': 'stage9'})
        elif wzd_brw.state == 'stage11':
            wzd_brw.write({'state': 'stage10'})
        elif wzd_brw.state == 'stage12':
            wzd_brw.write({'state': 'stage11'})
        elif wzd_brw.state == 'stage13':
            wzd_brw.write({'state': 'stage12'})
        elif wzd_brw.state == 'stage14':
            wzd_brw.write({'state': 'stage13'})
        elif wzd_brw.state == 'stage15':
            wzd_brw.write({'state': 'stage14'})
        elif wzd_brw.state == 'stage16':
            wzd_brw.write({'state': 'stage15'})
        elif wzd_brw.state == 'stage17':
            wzd_brw.write({'state': 'stage16'})
        elif wzd_brw.state == 'stage18':
            wzd_brw.write({'state': 'stage17'})
        elif wzd_brw.state == 'stage19':
            wzd_brw.write({'state': 'stage18'})
        elif wzd_brw.state == 'stage20':
            wzd_brw.write({'state': 'stage19'})
        elif wzd_brw.state == 'stage21':
            wzd_brw.write({'state': 'stage20'})
        return {}

    def prepare_chart(self, cr, uid, ids, context=None):
        context = context or {}
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        context['company_id'] = wzd_brw.company_id.id
        acc_obj = self.pool.get('account.account')
        # TODO: CHECK THAT CLOSED ACCOUNTS REMAIN CLOSED
        if wzd_brw.state == 'stage1':
            view_ids = acc_obj.search(cr, uid, [
                ('parent_id', 'child_of', wzd_brw.root_id.id),
                ('type', '=', 'view'),
                ('user_type.close_method', '!=', 'none'),
                ('active', '=', True),
            ], context=context)
            wzd_brw.write(
                {'state': 'stage2', 'account_ids': [(6, 0, view_ids)]})
        elif wzd_brw.state == 'stage2':
            res = [i.id for i in wzd_brw.account_ids]
            acc_obj.write(cr, uid, res,
                          {'user_type': wzd_brw.view_ut_id.id}, context=context)
            wzd_brw.write({'state': 'stage3', 'account_ids': [(6, 0, [])]})
        elif wzd_brw.state == 'stage3':
            view_ids = acc_obj.search(cr, uid, [
                ('parent_id', 'child_of',
                 [i.id for i in wzd_brw.bs_ids]),
                ('type', '!=', 'view'),
                ('user_type.close_method', '=', 'none'),
                ('active', '=', True),
            ], context=context)
            wzd_brw.write(
                {'state': 'stage4', 'account_ids': [(6, 0, view_ids)]})
        elif wzd_brw.state == 'stage4':
            res = [i.id for i in wzd_brw.account_ids]
            acc_obj.write(cr, uid, res,
                          {'user_type': wzd_brw.bs_ut_id.id}, context=context)
            is_ids = acc_obj.search(cr, uid, [
                ('parent_id', '=', wzd_brw.root_id.id),
                ('id', 'not in', [i.id for i in wzd_brw.bs_ids]),
                ('active', '=', True),
            ], context=context)
            wzd_brw.write({
                'state': 'stage5',
                'account_ids': [(6, 0, [])],
                'is_ids': [(6, 0, is_ids)],
            })
        elif wzd_brw.state == 'stage5':
            view_ids = acc_obj.search(cr, uid, [
                ('parent_id', 'child_of',
                 [i.id for i in wzd_brw.is_ids]),
                ('type', '!=', 'view'),
                '|', ('type', 'not in', ('other', 'closed')),
                ('user_type.close_method', '!=', 'none'),
                ('active', '=', True),
            ], context=context)
            wzd_brw.write(
                {'state': 'stage6', 'account_ids': [(6, 0, view_ids)]})
        elif wzd_brw.state == 'stage6':
            res = [i.id for i in wzd_brw.account_ids]
            acc_obj.write(cr, uid, res,
                          {'user_type': wzd_brw.is_ut_id.id,
                           'type': 'other'}, context=context)
            wzd_brw.write({'state': 'stage7', 'account_ids': [(6, 0, [])]})
        elif wzd_brw.state == 'stage7':
            view_ids = acc_obj.search(cr, uid, [
                ('parent_id', 'child_of',
                 [i.id for i in wzd_brw.bk_ids]),
                ('type', '!=', 'view'),
                '|', ('type', '!=', 'liquidity'),
                ('user_type.close_method', '!=', 'balance'),
                ('active', '=', True),
            ], context=context)
            wzd_brw.write(
                {'state': 'stage8', 'account_ids': [(6, 0, view_ids)]})
        elif wzd_brw.state == 'stage8':
            res = [i.id for i in wzd_brw.account_ids]
            acc_obj.write(cr, uid, res, {
                          'user_type': wzd_brw.bk_ut_id.id,
                          'type': 'liquidity',
                          }, context=context)
            bank_ids1x = acc_obj.search(cr, uid, [
                                        ('parent_id', 'child_of',
                                            [i.id for i in wzd_brw.bk_ids]),
                                        ('type', '!=', 'view'),
                                        ('active', '=', True),
                                        ], context=context)
            bank_ids2 = acc_obj.search(cr, uid, [
                ('parent_id', 'child_of', wzd_brw.root_id.id),
                ('id', 'not in', bank_ids1x),
                ('type', '!=', 'view'),
                ('type', '=', 'liquidity'),
                ('active', '=', True),
            ], context=context)
            wzd_brw.write(
                {'state': 'stage9', 'account_ids': [(6, 0, bank_ids2)]})
        elif wzd_brw.state == 'stage9':
            res = [i.id for i in wzd_brw.account_ids]
            acc_obj.write(cr, uid, res,
                          {'type': 'other'}, context=context)
            wzd_brw.write({'state': 'stage10', 'account_ids': [(6, 0, [])]})
        elif wzd_brw.state == 'stage10':
            view_ids = acc_obj.search(cr, uid, [
                ('parent_id', 'child_of',
                 [i.id for i in wzd_brw.rec_ids]),
                ('type', '!=', 'view'),
                '|', ('reconcile', '=', False),
                '|', ('type', 'not in', ('receivable', 'closed')),
                ('user_type.close_method', '!=', 'unreconciled'),
                ('active', '=', True),
            ], context=context)
            wzd_brw.write(
                {'state': 'stage11', 'account_ids': [(6, 0, view_ids)]})
        elif wzd_brw.state == 'stage11':
            res = [i.id for i in wzd_brw.account_ids]
            acc_obj.write(cr, uid, res, {
                          'user_type': wzd_brw.rec_ut_id.id,
                          'type': 'receivable',
                          'reconcile': True,
                          }, context=context)
            rec_ids1x = acc_obj.search(cr, uid, [
                ('parent_id', 'child_of',
                 [i.id for i in wzd_brw.rec_ids]),
                ('type', '!=', 'view'),
                ('active', '=', True),
            ], context=context)
            rec_ids2 = acc_obj.search(cr, uid, [
                ('parent_id', 'child_of', wzd_brw.root_id.id),
                ('id', 'not in', rec_ids1x),
                ('type', '!=', 'view'),
                ('type', '=', 'receivable'),
                ('active', '=', True),
            ], context=context)
            wzd_brw.write(
                {'state': 'stage12', 'account_ids': [(6, 0, rec_ids2)]})
        elif wzd_brw.state == 'stage12':
            res = [i.id for i in wzd_brw.account_ids]
            acc_obj.write(cr, uid, res,
                          {'type': 'other'}, context=context)
            wzd_brw.write({'state': 'stage13', 'account_ids': [(6, 0, [])]})
        elif wzd_brw.state == 'stage13':
            view_ids = acc_obj.search(cr, uid, [
                ('parent_id', 'child_of',
                 [i.id for i in wzd_brw.pay_ids]),
                ('type', '!=', 'view'),
                '|', ('reconcile', '=', False),
                '|', ('type', 'not in', ('payable', 'closed')),
                ('user_type.close_method', '!=', 'unreconciled'),
                ('active', '=', True),
            ], context=context)
            wzd_brw.write(
                {'state': 'stage14', 'account_ids': [(6, 0, view_ids)]})
        elif wzd_brw.state == 'stage14':
            res = [i.id for i in wzd_brw.account_ids]
            acc_obj.write(cr, uid, res, {
                          'user_type': wzd_brw.pay_ut_id.id,
                          'type': 'payable',
                          'reconcile': True,
                          }, context=context)
            pay_ids1x = acc_obj.search(cr, uid, [
                ('parent_id', 'child_of',
                 [i.id for i in wzd_brw.pay_ids]),
                ('type', '!=', 'view'),
                ('active', '=', True),
            ], context=context)
            pay_ids2 = acc_obj.search(cr, uid, [
                ('parent_id', 'child_of', wzd_brw.root_id.id),
                ('id', 'not in', pay_ids1x),
                ('type', '!=', 'view'),
                ('type', '=', 'payable'),
                ('active', '=', True),
            ], context=context)
            wzd_brw.write(
                {'state': 'stage15', 'account_ids': [(6, 0, pay_ids2)]})
        elif wzd_brw.state == 'stage15':
            res = [i.id for i in wzd_brw.account_ids]
            acc_obj.write(cr, uid, res,
                          {'type': 'other'}, context=context)
            wzd_brw.write({'state': 'stage16', 'account_ids': [(6, 0, [])]})
        elif wzd_brw.state == 'stage16' and wzd_brw.skip:
            wzd_brw.write({'state': 'stage18', 'skip': False})
        elif wzd_brw.state == 'stage16' and not wzd_brw.skip:
            acc_obj.write(cr, uid, [i.id for i in wzd_brw.recon_ids], {
                          'user_type': wzd_brw.recon_ut_id.id,
                          'type': 'other',
                          'reconcile': True,
                          }, context=context)
            view_ids = acc_obj.search(cr, uid, [
                ('parent_id', 'child_of',
                 [i.id for i in wzd_brw.bs_ids]),
                '!', ('parent_id', 'child_of',
                      [i.id for i in wzd_brw.bk_ids]),
                '!', ('parent_id', 'child_of',
                      [i.id for i in wzd_brw.rec_ids]),
                '!', ('parent_id', 'child_of',
                      [i.id for i in wzd_brw.pay_ids]),
                '!', ('id', 'in',
                      [i.id for i in wzd_brw.recon_ids]),
                ('type', '!=', 'view'),
                ('reconcile', '=', True),
                ('user_type.close_method', '=', 'unreconciled'),
                ('active', '=', True),
            ], context=context)
            wzd_brw.write(
                {'state': 'stage17', 'account_ids': [(6, 0, view_ids)]})
        elif wzd_brw.state == 'stage17':
            res = [i.id for i in wzd_brw.account_ids]
            acc_obj.write(cr, uid, res, {
                          'user_type': wzd_brw.bs_ut_id.id,
                          'type': 'other',
                          'reconcile': False,
                          }, context=context)
            wzd_brw.write({'state': 'stage18', 'account_ids': [(6, 0, [])]})
        elif wzd_brw.state == 'stage18' and wzd_brw.skip:
            wzd_brw.write({'state': 'stage20', 'skip': False})
        elif wzd_brw.state == 'stage18' and not wzd_brw.skip:
            acc_obj.write(cr, uid, [i.id for i in wzd_brw.det_ids], {
                          'user_type': wzd_brw.det_ut_id.id,
                          'type': 'other',
                          }, context=context)
            view_ids = acc_obj.search(cr, uid, [
                ('parent_id', 'child_of',
                 [i.id for i in wzd_brw.bs_ids]),
                '!', ('parent_id', 'child_of',
                      [i.id for i in wzd_brw.bk_ids]),
                '!', ('parent_id', 'child_of',
                      [i.id for i in wzd_brw.rec_ids]),
                '!', ('parent_id', 'child_of',
                      [i.id for i in wzd_brw.pay_ids]),
                '!', ('id', 'in',
                      [i.id for i in wzd_brw.recon_ids]),
                '!', ('id', 'in',
                      [i.id for i in wzd_brw.det_ids]),
                ('type', '!=', 'view'),
                ('user_type.close_method', '=', 'detail'),
                ('active', '=', True),
            ], context=context)
            wzd_brw.write(
                {'state': 'stage19', 'account_ids': [(6, 0, view_ids)]})
        elif wzd_brw.state == 'stage19':
            res = [i.id for i in wzd_brw.account_ids]
            acc_obj.write(cr, uid, res, {
                          'user_type': wzd_brw.bs_ut_id.id,
                          'type': 'other',
                          'reconcile': False,
                          }, context=context)
            wzd_brw.write({
                'state': 'stage20',
                'account_ids': [(6, 0, [])],
                'cons_ids': [(6, 0, [i.id for i in wzd_brw.is_ids])]})
        elif wzd_brw.state == 'stage20' and wzd_brw.skip:
            wzd_brw.write({'state': 'stage21', 'skip': False})
        elif wzd_brw.state == 'stage20' and not wzd_brw.skip:
            acc_obj.write(cr, uid, wzd_brw.cons_id.id, {
                'child_consol_ids': [(6, 0, [i.id for i in wzd_brw.cons_ids])]
            }, context=context)
            wzd_brw.write({
                'state': 'stage21',
                'account_ids': [(6, 0, [])]})

        return {}
