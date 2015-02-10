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
import openerp.addons.decimal_precision as dp # pylint: disable=F0401
import openerp


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
            'Unrealized Gain(+) or Loss(-)',
            digits_compute=dp.get_precision('Account'),
            help=("Value of Loss or Gain due to changes in exchange rate when "
                  "doing multi-currency transactions.")),
        'type': fields.related(
            'account_id', 'type',
            type='selection',
            selection=[('receivable', 'Receivable'),
                       ('payable', 'Payable'),
                       ('liquidity', 'Liquidity')],
            string='Internal Type',
            required=False,
            help=("The 'Internal Type' is used for features available on "
                  "different types of accounts: "
                  "payable/receivable are for partners accounts (for "
                  "debit/credit computations), liquidity for bank & cash")),
    }


class foreign_exchange_realization(osv.osv_memory):

    _name = 'foreign.exchange.realization'
    _rec_name = 'root_id'

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
                    "('company_id','=',company_id),"
                    "('currency_id','!=',False)]"),
            help=('Select your Bank Accounts')),
        'rec_ids': fields.many2many(
            'account.account', 'act_rec_acc_rel',
            'account_id', 'act_id', 'Receivable Accounts',
            domain=("[('type','=','receivable'),"
                    "('parent_id','child_of',root_id),"
                    "('company_id','=',company_id),"
                    "('currency_id','!=',False)]"),
            help=('Select your Receivable Accounts')),
        'pay_ids': fields.many2many(
            'account.account', 'act_pay_acc_rel',
            'account_id', 'act_id', 'Payable Accounts',
            domain=("[('type','=','payable'),"
                    "('parent_id','child_of',root_id),"
                    "('company_id','=',company_id),"
                    "('currency_id','!=',False)]"),
            help=('Select your Payable Accounts')),
        'fiscalyear_id': fields.many2one(
            'account.fiscalyear', 'Fiscal Year',
            required=True,
            domain="[('company_id','=',company_id)]",
            help='Fiscal Year'),
        'period_id': fields.many2one(
            'account.period', 'Period',
            required=True,
            domain=("[('fiscalyear_id','=',fiscalyear_id),"
                    "('company_id','=',company_id),"
                    "('special','=',False)]"),
            help=('Select your Payable Accounts')),
        'company_id': fields.many2one(
            'res.company', 'Company', required=True),
        'currency_id': fields.related(
            'company_id', 'currency_id',
            type='many2one',
            relation='res.currency',
            required=False,
            readonly=True,
            string='Company Currency',
            help="This is currency used to post Exchange Rate Difference"),
        'period_ids': fields.many2many(
            'account.period', 'act_period_acc_rel',
            'period_id', 'act_id', 'Affected Periods',
            readonly=True,
            help=('List of Affected Periods')),
        'date': fields.related(
            'period_id', 'date_stop',
            string='Posting Date',
            type='date',
            readonly=True,
            required=False),
        'journal_id': fields.many2one(
            'account.journal', 'Posting Journal',
            domain="[('company_id','=',company_id)]",
            required=False),
        'line_ids': fields.one2many(
            'foreign.exchange.realization.line',
            'wizard_id',
            'Suggested Recognition Lines'),
         'move_id': fields.many2one(
             'account.move', 'Journal Entry',
             required=False),
        'target_move': fields.selection(
            [('posted', 'All Posted Entries'),
            ('all', 'All Entries')],
            'Entries to Include',
            required=True,
            help='All Journal Entries or just Posted Journal Entries'),
        'state': fields.selection(
            [('draft', 'Draft'),
            ('open_fiscalyear', 'Open Fiscal Year'),
            ('missing_opening', 'Missing Opening Journal Entry'),
            ('in_progress', 'In Progress'),
            ('exception', 'Exception'),
            ('posted', 'Posted Journal'),
            ],
            'Entries to Include',
            required=True,
            help=(
            'Draft: Begin to fill required data to get Unrealized Values,\n'
            'Open Fiscal Year: Previous Fiscal Year is Open,\n'
            'Missing Opening Journal Entry: No Opening Journal Entry,\n'
            'In Progress: Unrealized Values has been fetched, ready to book,\n'
            'Exception: There are no Unrealized Values to book,\n'
            'Posted Journal: Unrealized Values have been booked'
            )),
    }

    _defaults = {
        'company_id': _get_default_company,
        'fiscalyear_id': _get_fiscalyear,
        'state': 'draft',
    }

    def get_values_from_aml(self, cr, uid, args, context=None):
        query = '''
            SELECT
                aml.account_id,
                aml.currency_id,
                SUM(aml.amount_currency) AS foreign_balance,
                SUM(aml.debit - aml.credit) AS balance
            FROM account_move_line AS aml
            INNER JOIN account_period AS ap ON ap.id = aml.period_id
            INNER JOIN account_move AS am ON am.id = aml.move_id
            WHERE
                aml.account_id IN (%(account_ids)s) AND
                aml.currency_id IS NOT NULL AND
                aml.state <> 'draft' AND
                am.state IN (%(states)s) AND
                ap.id IN (%(period_ids)s)
            GROUP BY aml.account_id, aml.currency_id
        ''' % args
        cr.execute(query)
        res = cr.dictfetchall()
        return res

    def get_accounts_from_aml(self, cr, uid, args, context=None):
        query = '''
            SELECT
                aml.account_id
            FROM account_move_line AS aml
            INNER JOIN account_account AS aa ON aa.id = aml.account_id
            INNER JOIN account_period AS ap ON ap.id = aml.period_id
            INNER JOIN account_move AS am ON am.id = aml.move_id
            WHERE
                aa.type = '%(account_type)s' AND
                aml.currency_id IS NOT NULL AND
                aml.state <> 'draft' AND
                am.state IN (%(states)s) AND
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

    def get_params(self, cr, uid, ids, account_type, fieldname, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        parent_left = wzd_brw.root_id.parent_left
        parent_right = wzd_brw.root_id.parent_right
        company_id = wzd_brw.company_id.id

        # Searching for other accounts that could be used as multicurrency
        states = ["'posted'"]
        if wzd_brw.target_move == 'all':
            states.append("'draft'")
        period_ids = [str(ap_brw.id) for ap_brw in wzd_brw.period_ids]
        if not period_ids:
            raise osv.except_osv(
                _('Error!'),
                _('There are no Periods selected'))
        args = dict(
            account_type=account_type,
            company_id=company_id,
            parent_left=parent_left,
            parent_right=parent_right,
            period_ids=', '.join(period_ids),
            states=', '.join(states),
        )
        return args

    def action_get_accounts(self, cr, uid, ids, account_type, fieldname,
                            context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        aa_obj = self.pool.get('account.account')
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        root_id = wzd_brw.root_id.id
        company_id = wzd_brw.company_id.id
        res = aa_obj.search(
            cr, uid, [
                ('type', '=', account_type),
                ('currency_id', '!=', False),
                ('parent_id', 'child_of', root_id),
                ('company_id', '=', company_id),
            ])

        # Searching for other accounts that could be used as multicurrency
        args = self.get_params(cr, uid, ids, account_type, fieldname,
                               context=context)
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

    def action_get_unrecognized_lines(self, cr, uid, ids, context=None):
        context = context or {}
        cur_obj = self.pool.get('res.currency')
        ferl_obj = self.pool.get('foreign.exchange.realization.line')
        ids = isinstance(ids, (int, long)) and [ids] or ids

        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        wzd_brw.line_ids.unlink()

        account_ids = []
        for fn in ('bk_ids', 'rec_ids', 'pay_ids'):
            account_ids += [aa_brw.id for aa_brw in getattr(wzd_brw, fn)]
        if not account_ids:
            raise osv.except_osv(
                _('Error!'),
                _('There are no accounts to compute'))

        account_ids = [str(idx) for idx in account_ids]

        states = ["'posted'"]
        if wzd_brw.target_move == 'all':
            states.append("'draft'")
        period_ids = [str(ap_brw.id) for ap_brw in wzd_brw.period_ids]

        args = dict(
            account_ids=', '.join(account_ids),
            period_ids=', '.join(period_ids),
            states=', '.join(states),
        )

        res = self.get_values_from_aml(cr, uid, args, context=context)
        context['date'] = wzd_brw.date
        for values in res:
            values['wizard_id'] = wzd_brw.id
            exchange_rate = cur_obj._get_current_rate(
                cr, uid, [values['currency_id']], context=context)
            values['exchange_rate'] = exchange_rate.get(values['currency_id'])
            values['adjusted_balance'] = \
                values['foreign_balance'] / values['exchange_rate']
            values['unrealized_gain_loss'] = \
                values['adjusted_balance'] - values['balance']
            ferl_obj.create(cr, uid, values, context=context)
        return True

    def account_move_get(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids

        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        ref = _("Exch. Curr. Rate Diff. for %s") %\
            (wzd_brw.period_id.name,)
        return self.pool.get('account.move').account_move_prepare(
            cr, uid, wzd_brw.journal_id.id, date=wzd_brw.date, ref=ref,
            company_id=wzd_brw.company_id.id, context=context)

    def line_get(self, cr, uid, line_brw, context=None):
        name = (_("Exch. Curr. Rate Diff. for %s in %s")
                % (line_brw.account_id.name, line_brw.currency_id.name))
        account_id = line_brw.account_id.id
        currency_id = line_brw.currency_id.id
        amount = line_brw.unrealized_gain_loss
        res_a = {
            'name': name[:64],
            'debit': amount > 0 and amount,
            'credit': amount < 0 and -amount,
            'account_id': account_id,
            'amount_currency': 0,
            'currency_id': currency_id,
        }
        company_brw = line_brw.wizard_id.company_id
        account_id = None
        if amount > 0:
            account_id = company_brw.income_currency_exchange_account_id and \
                company_brw.income_currency_exchange_account_id.id
        else:
            account_id = company_brw.expense_currency_exchange_account_id and \
                company_brw.expense_currency_exchange_account_id.id

        res_b = {
            'name': name[:64],
            'debit': amount < 0 and -amount,
            'credit': amount > 0 and amount,
            'account_id': account_id,
            'amount_currency': 0,
            'currency_id': currency_id,
        }
        return res_a, res_b

    def move_line_get(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        res = []
        for line_brw in wzd_brw.line_ids:
            res_a, res_b = self.line_get(cr, uid, line_brw, context=context)
            res.append((0, 0, res_a))
            res.append((0, 0, res_b))
        return res

    def check_gain_loss_account_company(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        company_brw = self.browse(cr, uid, ids[0], context=context).company_id

        action_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'account', 'action_account_form')[1]

        account_id = company_brw.income_currency_exchange_account_id and \
            company_brw.income_currency_exchange_account_id.id
        if not account_id:
            msg = _("You should configure the 'Loss Exchange Rate Account'"
                    " to manage automatically the booking of accounting "
                    "entries related to differences between exchange "
                    "rates.")
            raise openerp.exceptions.RedirectWarning(
                msg, action_id, _('Go to the configuration panel'))

        account_id = company_brw.expense_currency_exchange_account_id and \
            company_brw.expense_currency_exchange_account_id.id
        if not account_id:
            msg = _("You should configure the 'Gain Exchange Rate Account'"
                    "to manage automatically the booking of accounting "
                    "entries related to differences between exchange "
                    "rates.")
            raise openerp.exceptions.RedirectWarning(
                msg, action_id, _('Go to the configuration panel'))
        return True

    def create_move(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        if wzd_brw.move_id:
            raise osv.except_osv(
                _('Error!'),
                _('Gain & Loss Recognition already booked'))

        am_obj = self.pool.get('account.move')
        self.check_gain_loss_account_company(cr, uid, ids, context=context)

        move_vals = self.account_move_get(cr, uid, ids, context=context)
        move_id = am_obj.create(cr, uid, move_vals, context=context)
        lines = self.move_line_get(cr, uid, ids, context=context)
        am_obj.write(cr, uid, [move_id], {'line_id': lines}, context=context)
        wzd_brw.write({'move_id': move_id})

        if wzd_brw.journal_id.entry_posted:
            am_obj.button_validate(cr, uid, [move_id], context)
        return True
