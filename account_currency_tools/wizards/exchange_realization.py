# coding: utf-8
import logging
from datetime import datetime, timedelta
import pytz
from odoo import _, api, fields, models
import odoo.addons.decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Extra Imports
try:
    from pandas import DataFrame
except ImportError:
    _logger.info('account_currency_tools is declared '
                 ' from addons-vauxoo '
                 ' you will need: sudo pip install pandas')


class ForeignExchangeRealizationLine(models.TransientModel):

    _name = 'foreign.exchange.realization.line'

    wizard_id = fields.Many2one(
        'foreign.exchange.realization',
        string='Wizard',
        required=False,)
    account_id = fields.Many2one(
        'account.account', 'Account',
        required=True,)
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        required=True,)
    exchange_rate = fields.Float(
        'Exchange Rate',
        digits=(12, 6))
    balance = fields.Float(
        'Balance',
        digits=dp.get_precision('Account'))
    foreign_balance = fields.Float(
        'Foreign Balance',
        digits=dp.get_precision('Account'),
        help=("Total amount (in Secondary currency) for transactions held "
              "in secondary currency for this account."))
    adjusted_balance = fields.Float(
        'Adjusted Balance',
        digits=dp.get_precision('Account'),
        help=("Total amount (in Company currency) for transactions held "
              "in secondary currency for this account."))
    unrealized_gain_loss = fields.Float(
        'Unrealized Gain(+) or Loss(-)',
        digits=(2, 2),
        help=("Value of Loss or Gain due to changes in exchange rate when "
              "doing multi-currency transactions."))
    type = fields.Selection(
        related="account_id.internal_type",
        selection=[('receivable', 'Receivable'),
                   ('payable', 'Payable'),
                   ('liquidity', 'Liquidity')],
        string='Internal Type',
        required=False,
        help=("The 'Internal Type' is used for features available on "
              "different types of accounts: "
              "payable/receivable are for partners accounts (for "
              "debit/credit computations), liquidity for bank & cash"))


class ForeignExchangeRealization(models.TransientModel):

    _name = 'foreign.exchange.realization'

    def _get_default_company(self):
        company_id = self.env['res.users']._get_company()
        if not company_id:
            raise UserError(
                _('There is no default company for the current user!'))
        return company_id

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id:
            res = {}
            company = self.company_id

            if company.bank_gain_exchange_account_id:
                res.update(
                    {'bank_gain_exchange_account_id':
                     company.bank_gain_exchange_account_id.id})
            if company.bank_loss_exchange_account_id:
                res.update(
                    {'bank_loss_exchange_account_id':
                     company.bank_loss_exchange_account_id.id})
            if company.rec_gain_exchange_account_id:
                res.update(
                    {'rec_gain_exchange_account_id':
                     company.rec_gain_exchange_account_id.id})
            if company.rec_loss_exchange_account_id:
                res.update(
                    {'rec_loss_exchange_account_id':
                     company.rec_loss_exchange_account_id.id})
            if company.pay_gain_exchange_account_id:
                res.update(
                    {'pay_gain_exchange_account_id':
                     company.pay_gain_exchange_account_id.id})
            if company.pay_loss_exchange_account_id:
                res.update(
                    {'pay_loss_exchange_account_id':
                     company.pay_loss_exchange_account_id.id})
            if company.income_currency_exchange_account_id:
                res.update(
                    {'income_currency_exchange_account_id':
                     company.income_currency_exchange_account_id.id})
            if company.expense_currency_exchange_account_id:
                res.update(
                    {'expense_currency_exchange_account_id':
                     company.expense_currency_exchange_account_id.id})
            journal = (company.journal_id or
                       company.currency_exchange_journal_id)
            if journal:
                res.update(
                    {'journal_id': journal.id})

            res.update({
                'currency_id': company.currency_id.id,
                'check_non_multicurrency_account':
                company.check_non_multicurrency_account})
            self.update(res)
            if res.get('journal_id', False):
                self.onchange_journal_id()

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            res = {}
            journal = self.journal_id

            if journal.default_credit_account_id:
                res.update(
                    {'income_currency_exchange_account_id':
                     journal.default_credit_account_id.id})
            if journal.default_debit_account_id:
                res.update(
                    {'expense_currency_exchange_account_id':
                     journal.default_debit_account_id.id})
            self.update(res)

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        readonly=True,
        default=_default_company,
        states={'draft': [('readonly', False)]})
    bk_ids = fields.Many2many(
        'account.account', 'act_bk_acc_rel',
        'account_id', 'act_id', 'Bank & Cash Accounts',
        domain=([('internal_type','=','liquidity'),
                 ('currency_id','!=',False)]),
        help=('Select your Bank Accounts'))
    bank_gain_exchange_account_id = fields.Many2one(
        'account.account', 'Bank Gain Exchange Rate Account',
        required=False,
        help=('Bank Gain Exchange Rate Account for booking '
              'Difference'))
    bank_loss_exchange_account_id = fields.Many2one(
        'account.account', 'Bank Loss Exchange Rate Account',
        required=False,
        help=('Bank Loss Exchange Rate Account for booking '
              'Difference'))
    rec_ids = fields.Many2many(
        'account.account', 'act_rec_acc_rel',
        'account_id', 'act_id', 'Receivable Accounts',
        domain=([('internal_type','=','receivable'),
                 ('currency_id','!=',False)]),
        help=('Select your Receivable Accounts'))
    rec_gain_exchange_account_id = fields.Many2one(
        'account.account', 'Receivable Gain Exchange Rate Account',
        required=False,
        help=('Receivable Gain Exchange Rate Account for booking '
              'Difference'))
    rec_loss_exchange_account_id = fields.Many2one(
        'account.account', 'Receivable Loss Exchange Rate Account',
        required=False,
        help=('Receivable Loss Exchange Rate Account for booking '
              'Difference'))
    pay_ids = fields.Many2many(
        'account.account', 'act_pay_acc_rel',
        'account_id', 'act_id', 'Payable Accounts',
        domain=([('internal_type','=','payable'),
                 ('currency_id','!=',False)]),
        help=('Select your Payable Accounts'))
    pay_gain_exchange_account_id = fields.Many2one(
        'account.account', 'Payable Gain Exchange Rate Account',
        required=False,
        help=('Payable Gain Exchange Rate Account for booking '
              'Difference'))
    pay_loss_exchange_account_id = fields.Many2one(
        'account.account', 'Payable Loss Exchange Rate Account',
        required=False,
        help=('Payable Loss Exchange Rate Account for booking '
              'Difference'))
    currency_id = fields.Many2one(
        related='company_id.currency_id',
        relation='res.currency',
        required=False,
        readonly=True,
        string='Company Currency',
        help="This is currency used to post Exchange Rate Difference")
    check_non_multicurrency_account = fields.Boolean(
        related='company_id.check_non_multicurrency_account',
        readonly=True,
        string='Check Non-Multicurrency Account',
        help="Check Accounts that were not set as multicurrency, "
        "i.e., they were not set with a secondary currency, "
        "but were involved in multicurrency transactions")
    date = fields.Date(
        string='Posting Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one(
        'account.journal', 'Posting Journal',
        domain=([('type','=','general')]),
        required=True)
    line_ids = fields.One2many(
        'foreign.exchange.realization.line',
        'wizard_id',
        'Suggested Recognition Lines')
    move_id = fields.Many2one(
        'account.move',
        string='Realization Journal Entry',
        readonly=True,
        required=False)
    target_move = fields.Selection(
        [('posted', 'All Posted Entries'),
         ('all', 'All Entries')],
        'Entries to Include',
        required=True,
        default='posted',
        help='All Journal Entries or just Posted Journal Entries')
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('missing_opening', 'Missing Opening Journal Entry'),
            ('prepare', 'Preparing Data'),
            ('in_progress', 'In Progress'),
            ('exception', 'Exception'),
            ('posted', 'Posted Journal'),
        ],
        'Entries to Include',
        required=True,
        default='draft',
        help=(
            'Draft: Fill required data to get Unrealized Values,\n'
            'Missing Opening Journal Entry: No Opening Journal Entry,\n'
            'Preparing Data: Data to Fetch Unrealized Values has been set,\n'
            'In Progress: Unrealized Values has been fetched, ready to book,\n'
            'Exception: There are no Unrealized Values to book,\n'
            'Posted Journal: Unrealized Values have been booked'
        ))
    income_currency_exchange_account_id = fields.Many2one(
        'account.account',
        string="Gain Exchange Rate Account",
        domain=[('internal_type', '=', 'other')])
    expense_currency_exchange_account_id = fields.Many2one(
        'account.account',
        string="Loss Exchange Rate Account",
        domain=[('internal_type', '=', 'other')])
    skip_opening_entry = fields.Boolean(
        'Skip Opening Journal Entry Check')

    def get_account_balance(self, args):
        cr = self._cr
        query = '''
            SELECT
                aml.currency_id,
                SUM(aml.balance) AS balance
            FROM account_move_line AS aml
            INNER JOIN account_move AS am ON am.id = aml.move_id
            WHERE
                aml.account_id IN %(account_ids)s AND
                aml.currency_id IN %(currency_ids)s AND
                aml.currency_id IS NOT NULL AND
                aml.state <> 'draft' AND
                am.state IN %(states)s AND
                aml.date <= %(date)s
            GROUP BY aml.currency_id
        '''
        query = cr.mogrify(query, args)
        cr.execute(query)
        res = cr.dictfetchall()
        return res

    def get_values_from_aml(self, args):
        cr = self._cr
        query = '''
            SELECT
                aml.account_id,
                aml.currency_id,
                SUM(aml.amount_currency) AS foreign_balance,
                SUM(aml.balance) AS balance
            FROM account_move_line AS aml
            INNER JOIN account_move AS am ON am.id = aml.move_id
            WHERE
                aml.account_id IN %(account_ids)s AND
                aml.currency_id IS NOT NULL AND
                aml.state <> 'draft' AND
                am.state IN %(states)s AND
                aml.date <= %(date)s
            GROUP BY aml.account_id, aml.currency_id
        '''
        query = cr.mogrify(query, args)
        cr.execute(query)
        res = cr.dictfetchall()
        return res

    def get_accounts_from_aml(self, args):
        cr = self._cr
        query = '''
            SELECT
                aml.account_id
            FROM account_move_line AS aml
            INNER JOIN account_account AS aa ON aa.id = aml.account_id
            INNER JOIN account_move AS am ON am.id = aml.move_id
            WHERE
                aa.type = %(account_type)s AND
                aml.currency_id IS NOT NULL AND
                aml.state <> 'draft' AND
                am.state IN %(states)s AND
                aml.company_id = %(company_id)s AND
                aml.date <= %(date)s
            GROUP BY aml.account_id
        '''
        query = cr.mogrify(query, args)
        cr.execute(query)
        res = cr.fetchall()
        if res:
            res = [idx[0] for idx in res]
        return res

    def get_params(self, account_type, fieldname):
        company_id = self.company_id.id
        date = self.date

        # Searching for other accounts that could be used as multicurrency
        states = ['posted']
        if self.target_move == 'all':
            states.append('draft')
        args = dict(
            account_type=account_type,
            company_id=company_id,
            states=tuple(states),
            date=date,
        )
        return args

    def action_get_accounts(self, account_type, fieldname):
        aa_obj = self.env['account.account']
        company_id = self.company_id.id
        res = aa_obj.search(
            [
                ('internal_type', '=', account_type),
                ('currency_id', '!=', False),
                ('company_id', '=', company_id),
            ])

        # Searching for other accounts that could be used as multicurrency
        if self.check_non_multicurrency_account:
            args = self.get_params(
                ids, account_type, fieldname)
            res |= self.get_accounts_from_aml(args)

        if res:
            self.write({fieldname: [(6, self.id, res.ids)]})
        else:
            self.write(
                {fieldname: [(3, aa_brw.id) for aa_brw in
                             getattr(self, fieldname)]})
        return True

    def action_get_rec_accounts(self):
        return self.action_get_accounts(
            'receivable', 'rec_ids')

    def action_get_pay_accounts(self):
        return self.action_get_accounts(
            'payable', 'pay_ids')

    def action_get_bank_accounts(self):
        return self.action_get_accounts(
            'liquidity', 'bk_ids')

    def action_get_unrecognized_lines(self):
        cur_obj = self.env['res.currency']
        ferl_obj = self.env['foreign.exchange.realization.line']

        self.line_ids.unlink()

        account_ids = []
        for fn in ('bk_ids', 'rec_ids', 'pay_ids'):
            account_ids += [aa_brw.id for aa_brw in getattr(self, fn)]
        if not account_ids:
            raise UserError(
                _('There are no accounts to compute'))

        states = ['posted']
        if self.target_move == 'all':
            states.append('draft')

        args = dict(
            account_ids=tuple(account_ids),
            states=tuple(states),
            date=self.date
        )

        res = self.get_values_from_aml(args)

        for values in res:
            values['wizard_id'] = self.id
            values['exchange_rate'] = cur_obj.browse(
                values['currency_id']).with_context(
                {'date': self.date})._get_current_rate()
            values['adjusted_balance'] = \
                values['foreign_balance'] / values['exchange_rate']
            values['unrealized_gain_loss'] = \
                values['adjusted_balance'] - values['balance']
            ferl_obj.create(values)
        return True

    def account_move_get(self):
        ref = _("Exch. Curr. Rate Diff. for %s") %\
            (self.date,)
        return {
            'journal_id': self.journal_id.id,
            'date': self.date,
            'ref': ref,
            'company_id': self.company_id.id,
        }

    def line_get_dict(self, args):
        return {
            'name': args['name'][:64],
            'debit': args['amount'] > 0 and args['amount'],
            'credit': args['amount'] < 0 and -args['amount'],
            'account_id': args['account_id'],
            'amount_currency': 0,
            'currency_id': args['currency_id'],
        }

    def get_gain_loss_account_company(self):
        gain = self.income_currency_exchange_account_id and \
            self.income_currency_exchange_account_id.id
        loss = self.expense_currency_exchange_account_id and \
            self.expense_currency_exchange_account_id.id
        return {'gain': gain, 'loss': loss}

    def line_get(self, line_brw):
        name = (_("Exch. Curr. Rate Diff. for %s in %s")
                % (line_brw.account_id.name, line_brw.currency_id.name))
        amount = line_brw.unrealized_gain_loss
        currency_id = line_brw.currency_id.id

        account_a = line_brw.account_id.id
        gal_acc = self.get_gain_loss_account_company()
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
        res_a = self.line_get_dict(args)

        args['amount'] = -amount
        args['account_id'] = account_b
        res_b = self.line_get_dict(args)

        return res_a, res_b

    def move_line_get(self):
        res = []

        dict_acc = self.get_gain_loss_accounts()
        common_lines = []
        for line_brw in self.line_ids:
            if not abs(line_brw.unrealized_gain_loss):
                continue
            if line_brw.account_id.internal_type in dict_acc.keys():
                common_lines.append(line_brw.id)
                continue
            res_a, res_b = self.line_get(line_brw)
            res.append((0, 0, res_a))
            res.append((0, 0, res_b))
        res += self.move_line_redirect_get()
        partner_id = self.company_id.partner_id.id
        for record in res:
            record[2]['partner_id'] = partner_id
        return res

    def move_line_redirect_get(self):
        res = []

        dict_acc = self.get_gain_loss_accounts()
        if dict_acc.get('fix'):
            dict_acc.pop('fix')
        if not dict_acc:
            return res

        fieldnames = ['currency_id', 'type', 'unrealized_gain_loss']
        gal = self.line_ids.read(fieldnames, load=None)
        gal = [rec for rec in gal if rec.get('type') in dict_acc.keys()]
        if not gal:
            return res

        cur_obj = self.env['res.currency']

        gal_df = DataFrame(gal)
        gal_grouped = gal_df.groupby(['type', 'currency_id'])

        gal_agg = gal_grouped.sum()
        gal_dict = gal_agg.to_dict()

        gal_val = gal_dict.get('unrealized_gain_loss')

        name = _("Exch. Curr. Rate Diff. for %s in %s")
        mapping = {
            'liquidity': _('Liquidity'),
            'receivable': _('Receivable'),
            'payable': _('Payable'),
        }
        gal_acc = self.get_gain_loss_account_company()
        states = ['posted']
        if self.target_move == 'all':
            states.append('draft')

        for key, val in gal_val.items():
            internal_type, currency_id = key
            curr_brw = cur_obj.browse(currency_id)
            acc = dict_acc[internal_type]
            account_a = acc['gain'] if val > 0 else acc['loss']

            args = {
                'name': name % (mapping[internal_type], curr_brw.name),
                'amount': val,
                'account_id': account_a,
                'currency_id': currency_id,
            }
            res_a = self.line_get_dict(args)

            args['amount'] = -val
            args['account_id'] = gal_acc['gain'] if val > 0 else gal_acc['loss']  # noqa
            res_b = self.line_get_dict(args)

            res.append((0, 0, res_a))
            res.append((0, 0, res_b))

        return res

    def get_gain_loss_accounts(self):
        res = {'fix': []}

        # TODO: Improve code can be done with getattr
        bank_gain = self.bank_gain_exchange_account_id
        bank_loss = self.bank_loss_exchange_account_id
        if any([bank_gain, bank_loss]) and not all([bank_gain, bank_loss]):
            res['fix'].append(_('Bank'))
        elif all([bank_gain, bank_loss]):
            res['liquidity'] = {'gain': bank_gain.id, 'loss': bank_loss.id}

        rec_gain = self.rec_gain_exchange_account_id
        rec_loss = self.rec_loss_exchange_account_id
        if any([rec_gain, rec_loss]) and not all([rec_gain, rec_loss]):
            res['fix'].append(_('Receivable'))
        elif all([rec_gain, rec_loss]):
            res['receivable'] = {'gain': rec_gain.id, 'loss': rec_loss.id}

        pay_gain = self.pay_gain_exchange_account_id
        pay_loss = self.pay_loss_exchange_account_id
        if any([pay_gain, pay_loss]) and not all([pay_gain, pay_loss]):
            res['fix'].append(_('Payable'))
        elif all([pay_gain, pay_loss]):
            res['payable'] = {'gain': pay_gain.id, 'loss': pay_loss.id}

        return res

    def check_gain_loss_accounts(self, exception=False):
        res = self.get_gain_loss_accounts().get('fix')
        if res and not exception:
            if exception:
                return False
            raise UserError(
                _('Both Gain & Loss Accounts for %s have to be filled, \n'
                  'You can not fill one without filling the other') %
                (' and '.join(res)))
        return True

    def check_gain_loss_currency_exchange_accounts(self):
        if not self.income_currency_exchange_account_id:
            msg = _("You should configure the 'Loss Exchange Rate Account'"
                    " to manage automatically the booking of accounting "
                    "entries related to differences between exchange "
                    "rates.")
            raise UserError(msg)

        if not self.expense_currency_exchange_account_id:
            msg = _("You should configure the 'Gain Exchange Rate Account'"
                    "to manage automatically the booking of accounting "
                    "entries related to differences between exchange "
                    "rates.")
            raise UserError(msg)
        return True

    def create_move(self):
        if self.move_id:
            raise UserError(
                _('Gain & Loss Recognition already booked'))

        am_obj = self.env['account.move']
        self.check_gain_loss_currency_exchange_accounts()
        lines = self.move_line_get()
        if not lines:
            return False
        move_vals = self.account_move_get()
        move_id = am_obj.create(move_vals)
        move_id.write({'line_ids': lines})
        self.write({'move_id': move_id.id})

        return True

    def action_prepare(self):

        if self.move_id:
            raise UserError(
                _('There is already a Realization Journal Entry!'))

        self.action_get_rec_accounts()
        self.action_get_pay_accounts()
        self.action_get_bank_accounts()

        self.write({'state': 'prepare'})
        return True

    def action_progress(self):
        self.check_gain_loss_accounts()
        self.action_get_unrecognized_lines()

        self.write({'state': 'in_progress'})
        return True

    def action_create_move(self):
        res = self.create_move()

        state = 'posted'
        if not res:
            state = 'exception'
        self.write({'state': state})
        return True
