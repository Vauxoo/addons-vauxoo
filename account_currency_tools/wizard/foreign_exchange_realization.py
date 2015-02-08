#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# #############Credits#########################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your
#    option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class foreign_exchange_realization_line(osv.osv_memory):

    _name = 'foreign.exchange.realization.line'
    _columns = {
        'wizard_id': fields.many2one(
            'foreign.exchange.realization',
            string='Wizard',
            required=True,),
        'account_id': fields.many2one(
            'account.account', 'Account',
            required=True,),
        'currency_id': fields.many2one(
            'res.currency', 'Currency',
            required=True,),
        'exchange_rate': fields.float(
            'Exchange Rate',
            digits=(12, 6)),
        'balance': fields.float(
            'Balance',
            digits_compute=dp.get_precision('Account')),
        'foreign_balance': fields.float(
            'Foreign Balance',
            digits_compute=dp.get_precision('Account'),
            help=("Total amount (in Secondary currency) for transactions held "
                  "in secondary currency for this account.")),
        'adjusted_balance': fields.float(
            'Adjusted Balance',
            digits_compute=dp.get_precision('Account'),
            help=("Total amount (in Company currency) for transactions held "
                  "in secondary currency for this account.")),
        'unrealized_gain_loss': fields.float(
            'Unrealized Gain or Loss',
            digits_compute=dp.get_precision('Account'),
            help=("Value of Loss or Gain due to changes in exchange rate when "
                  "doing multi-currency transactions.")),
        'type': fields.selection([
            ('receivable', 'Receivable'),
            ('payable', 'Payable'),
            ('liquidity', 'Liquidity'),
        ],
            'Internal Type',
            required=True,
            help=("The 'Internal Type' is used for features available on "
                  "different types of accounts: "
                  "payable/receivable are for partners accounts (for "
                  "debit/credit computations), liquidity for bank & cash")),

    }


class foreign_exchange_realization(osv.osv_memory):

    _name = 'foreign.exchange.realization'

    def _get_fiscalyear(self, cr, uid, context=None):
        """Return default Fiscalyear value"""
        return self.pool.get('account.fiscalyear').find(
            cr, uid, exception=False, context=context)

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear_id=False,
                            context=None):
        res = {}
        res['value'] = {'period_id': False, 'period_ids': []}
        return res

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid,
                                                             context=context)
        if not company_id:
            raise osv.except_osv(
                _('Error!'),
                _('There is no default company for the current user!'))
        return company_id

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        if context is None:
            context = {}
        context['company_id'] = company_id
        res = {'value': {}}

        if not company_id:
            return res

        cur_id = self.pool.get('res.company').browse(
            cr, uid, company_id, context=context).currency_id.id
        res['value'].update({'currency_id': cur_id})
        return res

    _columns = {
        'help': fields.boolean(
            'Show Help', help='Allows you to toggle the help in the form'),
        'root_id': fields.many2one(
            'account.account', 'Root Account',
            domain=('[("company_id", "=", company_id), ("type", "=", "view"),'
                    '("parent_id", "=", None)]'),
            required=False,
            help=('Root Account, the account that plays as a'
                  'Chart of Accounts')),
        'bk_ids': fields.many2many(
            'account.account', 'act_bk_acc_rel',
            'account_id', 'act_id', 'Bank & Cash Accounts',
            domain=("[('type','=','liquidity'),"
                    "('parent_id','child_of',root_id),"
                    "('currency_id','!=',False)]"),
            help=('Select your Bank Accounts')),
        'rec_ids': fields.many2many(
            'account.account', 'act_rec_acc_rel',
            'account_id', 'act_id', 'Receivable Accounts',
            domain=("[('type','=','receivable'),"
                    "('parent_id','child_of',root_id),"
                    "('currency_id','!=',False)]"),
            help=('Select your Receivable Accounts')),
        'pay_ids': fields.many2many(
            'account.account', 'act_pay_acc_rel',
            'account_id', 'act_id', 'Payable Accounts',
            domain=("[('type','=','payable'),"
                    "('parent_id','child_of',root_id),"
                    "('currency_id','!=',False)]"),
            help=('Select your Payable Accounts')),
        'fiscalyear_id': fields.many2one(
            'account.fiscalyear', 'Fiscal Year',
            required=True,
            help='Fiscal Year'),
        'period_id': fields.many2one(
            'account.period', 'Period',
            required=True,
            domain=("[('fiscalyear_id','=',fiscalyear_id),"
                    "('special','=',False)]"),
            help=('Select your Payable Accounts')),
        'company_id': fields.many2one(
            'res.company', 'Company', required=True),
        'currency_id': fields.many2one(
            'res.currency', 'Company Currency',
            help="This is currency used to post Journal Entry Lines"),
        'period_ids': fields.many2many(
            'account.period', 'act_period_acc_rel',
            'period_id', 'act_id', 'Affected Periods',
            readonly=True,
            help=('List of Affected Periods')),
        'date': fields.related(
            'period_id', 'date_stop',
            string='Posting Date',
            type='date',
            required=False),
        'journal_id': fields.many2one(
            'account.journal', 'Posting Journal',
            required=False),
        'line_ids': fields.one2many(
            'foreign.exchange.realization.line',
            'wizard_id',
            'Suggested Recognition Lines',
        )
    }

    _defaults = {
        'company_id': _get_default_company,
        'fiscalyear_id': _get_fiscalyear,
    }


    def get_accounts_from_aml(self, cr, uid, args, context=None):
        query = '''
            SELECT
                aml.account_id
            FROM account_move_line AS aml
            INNER JOIN account_account AS aa ON aa.id = aml.account_id
            INNER JOIN account_period AS ap ON ap.id = aml.period_id
            WHERE
                aa.type = '%(account_type)s' AND
                aml.currency_id IS NOT NULL AND
                aml.company_id = %(company_id)d AND
                aa.id BETWEEN %(parent_left)d AND %(parent_right)d AND
                ap.id IN (%(period_ids)s)
            GROUP BY aml.account_id
        ''' % args
        cr.execute(query)
        res = cr.fetchall()
        if res:
            res = [idx[0] for idx in res]
        return res

    def action_get_accounts(self, cr, uid, ids, account_type, fieldname,
                            context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        aa_obj = self.pool.get('account.account')
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        root_id = wzd_brw.root_id.id
        parent_left = wzd_brw.root_id.parent_left
        parent_right = wzd_brw.root_id.parent_right
        company_id = wzd_brw.company_id.id
        res = aa_obj.search(
            cr, uid, [
                ('type', '=', account_type),
                ('currency_id', '!=', False),
                ('parent_id', 'child_of', root_id),
                ('company_id', '=', company_id),
            ])

        # Searching for other accounts that could be used as multicurrency
        period_ids = [str(ap_brw.id) for ap_brw in wzd_brw.period_ids]
        args = dict(
            account_type=account_type,
            company_id=company_id,
            parent_left=parent_left,
            parent_right=parent_right,
            period_ids=', '.join(period_ids)
        )
        res += self.get_accounts_from_aml(cr, uid, args, context=context)
        res = list(set(res))

        if res:
            wzd_brw.write({fieldname: [(6, wzd_brw.id, res)]})
        else:
            wzd_brw.write(
                {fieldname: [(3, aa_brw.id) for aa_brw in
                             getattr(wzd_brw, fieldname)]})
        return True

    def action_get_rec_accounts(self, cr, uid, ids, context=None):
        return self.action_get_accounts(
            cr, uid, ids, 'receivable', 'rec_ids', context=context)

    def action_get_pay_accounts(self, cr, uid, ids, context=None):
        return self.action_get_accounts(
            cr, uid, ids, 'payable', 'pay_ids', context=context)

    def action_get_bank_accounts(self, cr, uid, ids, context=None):
        return self.action_get_accounts(
            cr, uid, ids, 'liquidity', 'bk_ids', context=context)

    def action_get_periods(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        ap_obj = self.pool.get('account.period')
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        date_start = wzd_brw.fiscalyear_id.date_start
        date_stop = wzd_brw.period_id.date_stop
        res = ap_obj.search(
            cr, uid, [
                ('date_start', '>=', date_start),
                ('date_stop', '<=', date_stop)])
        if res:
            wzd_brw.write({'period_ids': [(6, wzd_brw.id, res)]})
        else:
            wzd_brw.write(
                {'period_ids': [(3, ap_brw.id) for ap_brw in
                                wzd_brw.period_ids]})
        return True

    def create_move(self, cr, uid, ids, context=None):
        return True
