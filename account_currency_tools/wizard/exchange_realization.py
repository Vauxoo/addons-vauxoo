# coding: utf-8
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
import openerp.addons.decimal_precision as dp  # pylint: disable=F0401
import openerp
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
import logging

_logger = logging.getLogger(__name__)

# Extra Imports
try:
    from pandas import DataFrame
except ImportError:
    _logger.info('account_currency_tools is declared '
                 ' from addons-vauxoo '
                 ' you will need: sudo pip install pandas')


class ForeignExchangeRealizationLine(osv.osv_memory):

    _name = 'foreign.exchange.realization.line'
    _columns = {
        'wizard_id': fields.many2one(
            'foreign.exchange.realization',
            string='Wizard',
            required=False,),
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
            digits=(2, 2),
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


class ForeignExchangeRealization(osv.osv_memory):

    _name = 'foreign.exchange.realization'
    _rec_name = 'root_id'

    def _get_fiscalyear(self, cr, uid, context=None):
        """Return default Fiscalyear value"""
        return self.pool.get('account.fiscalyear').find(
            cr, uid, exception=False, context=context)

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear_id=False,
                            context=None):
        res = {}
        period_id = False
        fy_obj = self.pool.get('account.fiscalyear')
        if fiscalyear_id:
            new_fy_id = fy_obj.find(cr, uid, exception=False, context=context)
            if fiscalyear_id == new_fy_id:
                ctx = dict(context or {})
                ctx['account_period_prefer_normal'] = True
                period_id = self.pool.get('account.period').find(
                    cr, uid, context=ctx)
                period_id = period_id and period_id[0]

        res['value'] = {'period_id': period_id, 'period_ids': []}
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
        context = context and dict(context) or {}
        context['company_id'] = company_id
        res = {'value': {}}

        if not company_id:
            return res

        acc_obj = self.pool.get('account.account')
        args = [("company_id", "=", company_id),
                ("type", "=", "view"),
                ("parent_id", "=", None)]
        root_id = acc_obj.search(cr, uid, args, context=context)

        rc_brw = self.pool.get('res.company').browse(
            cr, uid, company_id, context=context)
        cur_id = rc_brw.currency_id.id

        if rc_brw.bank_gain_exchange_account_id:
            res['value'].update(
                {'bank_gain_exchange_account_id':
                 rc_brw.bank_gain_exchange_account_id.id})
        if rc_brw.bank_loss_exchange_account_id:
            res['value'].update(
                {'bank_loss_exchange_account_id':
                 rc_brw.bank_loss_exchange_account_id.id})
        if rc_brw.rec_gain_exchange_account_id:
            res['value'].update(
                {'rec_gain_exchange_account_id':
                 rc_brw.rec_gain_exchange_account_id.id})
        if rc_brw.rec_loss_exchange_account_id:
            res['value'].update(
                {'rec_loss_exchange_account_id':
                 rc_brw.rec_loss_exchange_account_id.id})
        if rc_brw.pay_gain_exchange_account_id:
            res['value'].update(
                {'pay_gain_exchange_account_id':
                 rc_brw.pay_gain_exchange_account_id.id})
        if rc_brw.pay_loss_exchange_account_id:
            res['value'].update(
                {'pay_loss_exchange_account_id':
                 rc_brw.pay_loss_exchange_account_id.id})
        if rc_brw.income_currency_exchange_account_id:
            res['value'].update(
                {'income_currency_exchange_account_id':
                 rc_brw.income_currency_exchange_account_id.id})
        if rc_brw.expense_currency_exchange_account_id:
            res['value'].update(
                {'expense_currency_exchange_account_id':
                 rc_brw.expense_currency_exchange_account_id.id})
        if rc_brw.journal_id:
            res['value'].update(
                {'journal_id':
                 rc_brw.journal_id.id})

        res['value'].update({'currency_id': cur_id})
        res['value'].update({'root_id': root_id and root_id[0]})
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
        'bank_gain_exchange_account_id': fields.many2one(
            'account.account', 'Bank Gain Exchange Rate Account',
            domain=('[("company_id", "=", company_id),'
                    '("type", "!=", "view"),'
                    '("parent_id","child_of",root_id)]'),
            required=False,
            help=('Bank Gain Exchange Rate Account for booking '
                  'Difference')),
        'bank_loss_exchange_account_id': fields.many2one(
            'account.account', 'Bank Loss Exchange Rate Account',
            domain=('[("company_id", "=", company_id),'
                    '("type", "!=", "view"),'
                    '("parent_id","child_of",root_id)]'),
            required=False,
            help=('Bank Loss Exchange Rate Account for booking '
                  'Difference')),
        'rec_ids': fields.many2many(
            'account.account', 'act_rec_acc_rel',
            'account_id', 'act_id', 'Receivable Accounts',
            domain=("[('type','=','receivable'),"
                    "('parent_id','child_of',root_id),"
                    "('company_id','=',company_id),"
                    "('currency_id','!=',False)]"),
            help=('Select your Receivable Accounts')),
        'rec_gain_exchange_account_id': fields.many2one(
            'account.account', 'Receivable Gain Exchange Rate Account',
            domain=('[("company_id", "=", company_id),'
                    '("type", "!=", "view"),'
                    '("parent_id","child_of",root_id)]'),
            required=False,
            help=('Receivable Gain Exchange Rate Account for booking '
                  'Difference')),
        'rec_loss_exchange_account_id': fields.many2one(
            'account.account', 'Receivable Loss Exchange Rate Account',
            domain=('[("company_id", "=", company_id),'
                    '("type", "!=", "view"),'
                    '("parent_id","child_of",root_id)]'),
            required=False,
            help=('Receivable Loss Exchange Rate Account for booking '
                  'Difference')),
        'pay_ids': fields.many2many(
            'account.account', 'act_pay_acc_rel',
            'account_id', 'act_id', 'Payable Accounts',
            domain=("[('type','=','payable'),"
                    "('parent_id','child_of',root_id),"
                    "('company_id','=',company_id),"
                    "('currency_id','!=',False)]"),
            help=('Select your Payable Accounts')),
        'pay_gain_exchange_account_id': fields.many2one(
            'account.account', 'Payable Gain Exchange Rate Account',
            domain=('[("company_id", "=", company_id),'
                    '("type", "!=", "view"),'
                    '("parent_id","child_of",root_id)]'),
            required=False,
            help=('Payable Gain Exchange Rate Account for booking '
                  'Difference')),
        'pay_loss_exchange_account_id': fields.many2one(
            'account.account', 'Payable Loss Exchange Rate Account',
            domain=('[("company_id", "=", company_id),'
                    '("type", "!=", "view"),'
                    '("parent_id","child_of",root_id)]'),
            required=False,
            help=('Payable Loss Exchange Rate Account for booking '
                  'Difference')),
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
                    "('state','=','draft'),"
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
            domain=("[('company_id','=',company_id),"
                    "('type','=','general')]"),
            required=False),
        'line_ids': fields.one2many(
            'foreign.exchange.realization.line',
            'wizard_id',
            'Suggested Recognition Lines'),
        'move_id': fields.related(
            'period_id', 'move_id',
            type='many2one',
            relation='account.move',
            string='Realization Journal Entry',
            readonly=True,
            required=False),
        'target_move': fields.selection(
            [('posted', 'All Posted Entries'),
             ('all', 'All Entries')],
            'Entries to Include',
            required=True,
            help='All Journal Entries or just Posted Journal Entries'),
        'state': fields.selection(
            [
                ('draft', 'Draft'),
                ('open_fiscalyear', 'Open Fiscal Year'),
                ('missing_opening', 'Missing Opening Journal Entry'),
                ('prepare', 'Preparing Data'),
                ('in_progress', 'In Progress'),
                ('exception', 'Exception'),
                ('posted', 'Posted Journal'),
            ],
            'Entries to Include',
            required=True,
            help=(
                'Draft: Fill required data to get Unrealized Values,\n'
                'Open Fiscal Year: Previous Fiscal Year is Open,\n'
                'Missing Opening Journal Entry: No Opening Journal Entry,\n'
                'Preparing Data: Data to Fetch Unrealized Values has been'
                ' set,\n'
                'In Progress: Unrealized Values has been fetched, ready to '
                'book,\n'
                'Exception: There are no Unrealized Values to book,\n'
                'Posted Journal: Unrealized Values have been booked'
            )),
        'income_currency_exchange_account_id': fields.many2one(
            'account.account',
            string="Gain Exchange Rate Account",
            domain="[('type', '=', 'other')]"),
        'expense_currency_exchange_account_id': fields.many2one(
            'account.account',
            string="Loss Exchange Rate Account",
            domain="[('type', '=', 'other')]"),
        'skip_close_fiscalyear': fields.boolean(
            'Skip Close Fiscal Year Check'),
        'skip_opening_entry': fields.boolean(
            'Skip Opening Journal Entry Check'),
    }

    _defaults = {
        'company_id': _get_default_company,
        'fiscalyear_id': _get_fiscalyear,
        'state': 'draft',
        'target_move': 'posted',
    }

    def get_account_balance(self, cr, uid, args, context=None):
        query = '''
            SELECT
                aml.currency_id,
                SUM(aml.debit - aml.credit) AS balance
            FROM account_move_line AS aml
            INNER JOIN account_period AS ap ON ap.id = aml.period_id
            INNER JOIN account_move AS am ON am.id = aml.move_id
            WHERE
                aml.account_id IN (%(account_ids)s) AND
                aml.currency_id IN (%(currency_ids)s) AND
                aml.currency_id IS NOT NULL AND
                aml.state <> 'draft' AND
                am.state IN (%(states)s) AND
                ap.id IN (%(period_ids)s)
            GROUP BY aml.currency_id
        ''' % args
        cr.execute(query)
        res = cr.dictfetchall()
        return res

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
                aa.parent_left >= %(parent_left)d AND
                aa.parent_right <= %(parent_right)d AND
                ap.id IN (%(period_ids)s)
            GROUP BY aml.account_id
        ''' % args
        cr.execute(query)
        res = cr.fetchall()
        if res:
            res = [idx[0] for idx in res]
        return res

    def get_params(self, cr, uid, ids, account_type, fieldname, context=None):
        context = dict(context or {})
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
        context = dict(context or {})
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
        context = dict(context or {})
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
        context = dict(context or {})
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

        # parse from string to datetime, Added 23:59:59 Because the rate to be
        # used is the last one on the date not the first
        # This date is at User's TimeZone it will later be converted onto UTC
        dt = datetime.strptime(wzd_brw.date + ' 23:59:59',
                               DEFAULT_SERVER_DATETIME_FORMAT)

        # convert back from user's timezone to UTC
        tz_name = (context.get('tz') or
                   self.pool['res.users'].read(
                       cr, openerp.SUPERUSER_ID, uid, ['tz'],
                       context=context)['tz'])
        if tz_name:
            try:
                user_tz = pytz.timezone(tz_name)
                utc = pytz.utc

                dt = user_tz.localize(dt).astimezone(utc)
            except ImportError:
                _logger.warn(
                    "Failed to convert the value for a field of the model"
                    " %s back from the user's timezone (%s) to UTC",
                    wzd_brw._name, tz_name,
                    exc_info=True)

        # format back to string
        context['date'] = dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
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
        context = dict(context or {})
        ids = isinstance(ids, (int, long)) and [ids] or ids

        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        ref = _("Exch. Curr. Rate Diff. for %s") %\
            (wzd_brw.period_id.name,)
        return self.pool.get('account.move').account_move_prepare(
            cr, uid, wzd_brw.journal_id.id, date=wzd_brw.date, ref=ref,
            company_id=wzd_brw.company_id.id, context=context)

    def line_get_dict(self, cr, uid, args, context=None):
        return {
            'name': args['name'][:64],
            'debit': args['amount'] > 0 and args['amount'],
            'credit': args['amount'] < 0 and -args['amount'],
            'account_id': args['account_id'],
            'amount_currency': 0,
            'currency_id': args['currency_id'],
        }

    def get_gain_loss_account_company(self, cr, uid, ids, context=None):
        context = dict(context or {})
        ids = isinstance(ids, (int, long)) and [ids] or ids

        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        gain = wzd_brw.income_currency_exchange_account_id and \
            wzd_brw.income_currency_exchange_account_id.id
        loss = wzd_brw.expense_currency_exchange_account_id and \
            wzd_brw.expense_currency_exchange_account_id.id
        return {'gain': gain, 'loss': loss}

    def line_get(self, cr, uid, line_brw, context=None):
        context = dict(context or {})
        wzd_brw = line_brw.wizard_id
        name = (_("Exch. Curr. Rate Diff. for %s in %s")
                % (line_brw.account_id.name, line_brw.currency_id.name))
        amount = line_brw.unrealized_gain_loss
        currency_id = line_brw.currency_id.id

        account_a = line_brw.account_id.id
        gal_acc = self.get_gain_loss_account_company(cr, uid, wzd_brw.id,
                                                     context=context)
        if amount > 0:
            account_b = gal_acc['gain']
        else:
            account_b = gal_acc['loss']

        args = {
            'name': name,
            'amount': amount,
            'account_id': account_a,
            'currency_id': currency_id,
        }
        res_a = self.line_get_dict(cr, uid, args, context=context)

        args['amount'] = -amount
        args['account_id'] = account_b
        res_b = self.line_get_dict(cr, uid, args, context=context)

        return res_a, res_b

    def move_line_get(self, cr, uid, ids, context=None):
        context = dict(context or {})
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        res = []

        dict_acc = self.get_gain_loss_accounts(cr, uid, ids, context=context)
        common_lines = []
        for line_brw in wzd_brw.line_ids:
            if not abs(line_brw.unrealized_gain_loss):
                continue
            if line_brw.account_id.type in dict_acc.keys():
                common_lines.append(line_brw.id)
                continue
            res_a, res_b = self.line_get(cr, uid, line_brw, context=context)
            res.append((0, 0, res_a))
            res.append((0, 0, res_b))
        res += self.move_line_redirect_get(cr, uid, ids, context=context)
        return res

    def move_line_redirect_get(self, cr, uid, ids, context=None):
        context = dict(context or {})
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = []

        dict_acc = self.get_gain_loss_accounts(cr, uid, ids, context=context)
        if dict_acc.get('fix'):
            dict_acc.pop('fix')
        if not dict_acc:
            return res

        wzd_brw = self.browse(cr, uid, ids[0], context=context)

        fieldnames = ['currency_id', 'type', 'unrealized_gain_loss']
        gal = wzd_brw.line_ids.read(fieldnames, load=None)
        gal = [rec for rec in gal if rec.get('type') in dict_acc.keys()]
        if not gal:
            return res

        cur_obj = self.pool.get('res.currency')

        gal_df = DataFrame(gal)
        gal_grouped = gal_df.groupby(['type', 'currency_id'])

        gal_agg = gal_grouped.sum()
        gal_dict = gal_agg.to_dict()

        gal_val = gal_dict.get('unrealized_gain_loss')

        name = _(u"Exch. Curr. Rate Diff. for %s in %s")
        mapping = {
            'liquidity': _('Liquidity'),
            'receivable': _('Receivable'),
            'payable': _('Payable'),
        }
        gal_acc = self.get_gain_loss_account_company(cr, uid, wzd_brw.id,
                                                     context=context)
        period_ids = [str(ap_brw.id) for ap_brw in wzd_brw.period_ids]
        states = ["'posted'"]
        if wzd_brw.target_move == 'all':
            states.append("'draft'")
        argx = {
            'account_ids': None,
            'currency_ids': None,
            'states': ', '.join(states),
            'period_ids': ', '.join(period_ids),
        }

        for key, val in gal_val.iteritems():
            internal_type, currency_id = key
            curr_brw = cur_obj.browse(cr, uid, currency_id, context=context)
            acc = dict_acc[internal_type]
            account_a = val > 0 and acc['gain'] or acc['loss']
            argx['account_ids'] = '%s, %s' % (
                str(acc['gain']), str(acc['loss']))
            argx['currency_ids'] = str(currency_id)

            res_acc = self.get_account_balance(cr, uid, argx, context=context)
            val_acc = res_acc and res_acc[0]['balance'] or 0.0
            val -= val_acc

            args = {
                'name': name % (mapping[internal_type], curr_brw.name),
                'amount': val,
                'account_id': account_a,
                'currency_id': currency_id,
            }
            res_a = self.line_get_dict(cr, uid, args, context=context)

            args['amount'] = -val
            args['account_id'] = val > 0 and gal_acc['gain'] or gal_acc['loss']
            res_b = self.line_get_dict(cr, uid, args, context=context)

            res.append((0, 0, res_a))
            res.append((0, 0, res_b))

        return res

    def get_gain_loss_accounts(self, cr, uid, ids, context=None):
        context = dict(context or {})
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        res = {'fix': []}

        # TODO: Improve code can be done with getattr
        bank_gain = wzd_brw.bank_gain_exchange_account_id
        bank_loss = wzd_brw.bank_loss_exchange_account_id
        if any([bank_gain, bank_loss]) and not all([bank_gain, bank_loss]):
            res['fix'].append(_('Bank'))
        elif all([bank_gain, bank_loss]):
            res['liquidity'] = {'gain': bank_gain.id, 'loss': bank_loss.id}

        rec_gain = wzd_brw.rec_gain_exchange_account_id
        rec_loss = wzd_brw.rec_loss_exchange_account_id
        if any([rec_gain, rec_loss]) and not all([rec_gain, rec_loss]):
            res['fix'].append(_('Receivable'))
        elif all([rec_gain, rec_loss]):
            res['receivable'] = {'gain': rec_gain.id, 'loss': rec_loss.id}

        pay_gain = wzd_brw.pay_gain_exchange_account_id
        pay_loss = wzd_brw.pay_loss_exchange_account_id
        if any([pay_gain, pay_loss]) and not all([pay_gain, pay_loss]):
            res['fix'].append(_('Payable'))
        elif all([pay_gain, pay_loss]):
            res['payable'] = {'gain': pay_gain.id, 'loss': pay_loss.id}

        return res

    def check_gain_loss_accounts(self, cr, uid, ids, exception=False,
                                 context=None):
        context = dict(context or {})
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = self.get_gain_loss_accounts(
            cr, uid, ids, context=context).get('fix')
        if res and not exception:
            if exception:
                return False
            raise osv.except_osv(
                _('Error!'),
                _('Both Gain & Loss Accounts for %s have to be filled, \n'
                  'You can not fill one without filling the other') %
                (' and '.join(res)))
        return True

    def check_gain_loss_account_company(self, cr, uid, ids, context=None):
        context = dict(context or {})
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        company_brw = wzd_brw.company_id

        action_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'account', 'action_account_form')[1]

        account_id = company_brw.income_currency_exchange_account_id and \
            company_brw.income_currency_exchange_account_id.id or \
            wzd_brw.income_currency_exchange_account_id and \
            wzd_brw.income_currency_exchange_account_id.id
        if not account_id:
            msg = _("You should configure the 'Loss Exchange Rate Account'"
                    " to manage automatically the booking of accounting "
                    "entries related to differences between exchange "
                    "rates.")
            raise openerp.exceptions.RedirectWarning(
                msg, action_id, _('Go to the configuration panel'))

        account_id = company_brw.expense_currency_exchange_account_id and \
            company_brw.expense_currency_exchange_account_id.id
        account_id = company_brw.expense_currency_exchange_account_id and \
            company_brw.expense_currency_exchange_account_id.id or \
            wzd_brw.expense_currency_exchange_account_id and \
            wzd_brw.expense_currency_exchange_account_id.id
        if not account_id:
            msg = _("You should configure the 'Gain Exchange Rate Account'"
                    "to manage automatically the booking of accounting "
                    "entries related to differences between exchange "
                    "rates.")
            raise openerp.exceptions.RedirectWarning(
                msg, action_id, _('Go to the configuration panel'))
        return True

    def create_move(self, cr, uid, ids, context=None):
        context = dict(context or {})
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        if wzd_brw.move_id:
            raise osv.except_osv(
                _('Error!'),
                _('Gain & Loss Recognition already booked'))

        am_obj = self.pool.get('account.move')
        self.check_gain_loss_account_company(cr, uid, ids, context=context)

        lines = self.move_line_get(cr, uid, ids, context=context)
        if not lines:
            return False
        move_vals = self.account_move_get(cr, uid, ids, context=context)
        move_id = am_obj.create(cr, uid, move_vals, context=context)
        am_obj.write(cr, uid, [move_id], {'line_id': lines}, context=context)
        wzd_brw.write({'move_id': move_id})

        if wzd_brw.journal_id.entry_posted:
            am_obj.button_validate(cr, uid, [move_id], context)
        return True

    def action_prepare(self, cr, uid, ids, context=None):
        context = dict(context or {})
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wzd_brw = self.browse(cr, uid, ids[0], context=context)

        if wzd_brw.move_id:
            raise osv.except_osv(
                _('Error!'),
                _('There is already a Realization Journal Entry in %s!') %
                wzd_brw.period_id.name)

        if not wzd_brw.skip_close_fiscalyear and \
                not self.check_previous_fiscalyear(cr, uid, ids,
                                                   context=context):
            return wzd_brw.write({'state': 'open_fiscalyear'})

        if not wzd_brw.skip_opening_entry and \
                not self.check_opening_journal_entry(cr, uid, ids,
                                                     context=context):
            return wzd_brw.write({'state': 'missing_opening'})

        self.action_get_periods(cr, uid, ids, context=context)
        self.action_get_rec_accounts(cr, uid, ids, context=context)
        self.action_get_pay_accounts(cr, uid, ids, context=context)
        self.action_get_bank_accounts(cr, uid, ids, context=context)

        wzd_brw.write({'state': 'prepare'})
        return True

    def action_progress(self, cr, uid, ids, context=None):
        context = dict(context or {})
        ids = isinstance(ids, (int, long)) and [ids] or ids

        self.check_gain_loss_accounts(cr, uid, ids, context=context)
        self.action_get_unrecognized_lines(cr, uid, ids, context=context)

        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        wzd_brw.write({'state': 'in_progress'})
        return True

    def check_opening_journal_entry(self, cr, uid, ids, context=None):
        context = dict(context or {})
        ids = isinstance(ids, (int, long)) and [ids] or ids
        ap_obj = self.pool.get('account.period')
        am_obj = self.pool.get('account.move')

        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        date_start = wzd_brw.fiscalyear_id.date_start
        company_id = wzd_brw.company_id.id

        period_id = ap_obj.search(
            cr, uid, [('date_start', '=', date_start),
                      ('special', '=', True)], context=context)

        period_id = period_id and period_id[0]

        if not period_id:
            return True

        args = [('date', '=', date_start),
                ('journal_id.type', '=', 'situation'),
                ('period_id', '=', period_id),
                ('company_id', '=', company_id),
                ]

        if wzd_brw.target_move == 'posted':
            args.append(('state', '=', 'posted'))

        return am_obj.search(cr, uid, args, context=context)

    def check_previous_fiscalyear(self, cr, uid, ids, context=None):
        context = dict(context or {})
        ids = isinstance(ids, (int, long)) and [ids] or ids

        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        fy_obj = self.pool.get('account.fiscalyear')

        date_start = wzd_brw.fiscalyear_id.date_start
        date_stop = (datetime.strptime(date_start, '%Y-%m-%d') -
                     timedelta(days=1))
        date_stop = date_stop.strftime('%Y-%m-%d')
        fy_id = fy_obj.find(
            cr, uid, dt=date_stop, exception=False, context=context)
        if not fy_id:
            return True
        return fy_obj.browse(cr, uid, fy_id, context=context).state == 'done'

    def action_create_move(self, cr, uid, ids, context=None):
        context = dict(context or {})
        ids = isinstance(ids, (int, long)) and [ids] or ids

        res = self.create_move(cr, uid, ids, context=context)

        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        if not res:
            wzd_brw.write({'state': 'exception'})
        else:
            wzd_brw.write({'state': 'posted'})
        return True
