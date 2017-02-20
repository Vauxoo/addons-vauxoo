# coding: utf-8
# #############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# ############ Credits ########################################################
#    Coded by: Katherine Zaoral          <kathy@vauxoo.com>
#    Planified by: Humberto Arocha       <hbto@vauxoo.com>
#    Audited by: Humberto Arocha         <hbto@vauxoo.com>
# #############################################################################
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
import time
from openerp.osv import fields, osv
from openerp import api, workflow
from openerp.addons import decimal_precision as dp
from openerp.tools.translate import _


class HrExpenseExpense(osv.Model):
    _inherit = "hr.expense.expense"

    def expense_canceled(self, cr, uid, ids, context=None):
        obj_move = self.pool.get('account.move')
        obj_move_rec = self.pool.get('account.move.reconcile')

        res = super(HrExpenseExpense,
                    self).expense_canceled(cr, uid, ids, context=context)
        for expense in self.browse(cr, uid, ids, context=context):
            if expense.account_move_id:
                reconcile_id = \
                    [move_line.reconcile_id.id
                     for move_line in expense.account_move_id.line_id
                     if move_line.reconcile_id]
                reconcile_partial_id = \
                    [move_line.reconcile_partial_id.id
                     for move_line in expense.account_move_id.line_id
                     if move_line.reconcile_partial_id]
                recs = reconcile_id + reconcile_partial_id
                all_moves_recs = list(set(recs))
                if all_moves_recs:
                    obj_move_rec.unlink(cr, uid, all_moves_recs)
                obj_move.unlink(cr, uid, [expense.account_move_id.id],
                                context=context)
        return res

    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        """ Overwrite method to add the sum of the invoices total amount
        (Sub total + tax amount ). """
        context = context or {}
        cur_obj = self.pool.get('res.currency')
        res = super(HrExpenseExpense, self)._amount(
            cr, uid, ids, field_name, arg, context=context)
        for expense in self.browse(cr, uid, res.keys(), context=context):
            for invoice in expense.invoice_ids:
                if expense.state in \
                        ('draft', 'confirm', 'accepted', 'cancelled'):
                    date = fields.date.today()
                else:
                    date = invoice.date_invoice
                res[expense.id] += cur_obj.exchange(
                    cr, uid, [],
                    from_amount=invoice.amount_total,
                    to_currency_id=expense.currency_id.id,
                    from_currency_id=invoice.currency_id.id,
                    exchange_date=date,
                    context=context)
        return res

    def _get_exp_from_invoice(self, cr, uid, ids, context=None):
        """ Return expense ids related to invoices that have been changed."""
        context = context or {}
        ai_obj = self.pool.get('account.invoice')
        inv_ids = ids
        exp_ids = list(set(
            [inv_brw.expense_id.id
             for inv_brw in ai_obj.browse(cr, uid, inv_ids, context=context)]))
        return exp_ids

    def _get_ait_ids(self, cr, uid, ids, field_name, arg, context=None):
        """ Returns list of invoice taxes of the invoices related to the
        expense. """
        context = context or {}
        res = {}.fromkeys(ids, [])
        for exp in self.browse(cr, uid, ids, context=context):
            ait_ids = []
            for inv_brw in exp.invoice_ids:
                ait_ids.extend([line.id for line in inv_brw.tax_line])
            res[exp.id] = ait_ids
        return res

    def _get_ail_ids(self, cr, uid, ids, field_name, arg, context=None):
        """ Returns list of invoice lines of the invoices related to the
        expense. """
        context = context or {}
        res = {}
        for exp in self.browse(cr, uid, ids, context=context):
            ail_ids = []
            for inv_brw in self.browse(
                    cr, uid, exp.id, context=context).invoice_ids:
                ail_ids.extend([line.id for line in inv_brw.invoice_line])
            res[exp.id] = ail_ids
        return res

    def her_entries(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = {}.fromkeys(ids, [])
        for exp in self.browse(cr, uid, ids, context=context):
            res[exp.id] += exp.account_move_id \
                and [move.id for move in exp.account_move_id.line_id] or []
            res[exp.id] += [line.id for line in exp.advance_ids]
            res[exp.id] += [line2.id for pay in exp.payment_ids
                            for line2 in pay.move_ids]
            for inv in exp.invoice_ids:
                if not inv.move_id:
                    continue
                for move2 in inv.move_id.line_id:
                    res[exp.id] += [move2.id]
        return res

    def _her_entries(self, cr, uid, ids, field_name, arg, context=None):
        context = context or {}
        return self.her_entries(cr, uid, ids, context=context)

    def _get_payment_status(self, cr, uid, ids, field_name, arg, context=None):
        context = context or {}
        res = {}.fromkeys(ids, False)
        rex = {}.fromkeys(ids, [])
        aml_obj = self.pool.get('account.move.line')
        for id_entrie, aml_ids in self.her_entries(
                cr, uid, ids, context=context).iteritems():
            if not aml_ids:
                continue
            for aml_brw in aml_obj.browse(cr, uid, aml_ids, context=context):
                if aml_brw.account_id.type not in ('payable', 'receivable'):
                    continue
                if aml_brw.reconcile_id:
                    continue
                rex[id_entrie] += [aml_brw.id]
        for id_item, aml_ids in rex.iteritems():
            exp_brw = self.browse(cr, uid, id_item, context=context)
            if exp_brw.state == 'paid' and not aml_ids:
                res[id_item] = True
            elif exp_brw.state == 'paid' and aml_ids:
                exp_brw.write({'state': 'process'})
            elif exp_brw.state == 'process' and not aml_ids:
                res[id_item] = True
                exp_brw.write({'state': 'paid'})
        return res

    _columns = {
        'partner_id': fields.related(
            'employee_id', 'address_home_id',
            string='Partner linked to Employee',
            help=('This field is automatically filled when Employee is '
                  'selected'),
            relation='res.partner', type='many2one', store=True,
            readonly=True),

        'invoice_ids': fields.one2many('account.invoice', 'expense_id',
                                       'Invoices', help=''),
        'ail_ids': fields.function(_get_ail_ids,
                                   type="one2many",
                                   relation='account.invoice.line',
                                   string='Invoices lines',
                                   help='Deductible Expense'),
        'amount': fields.function(
            _amount,
            string='Total Amount',
            digits_compute=dp.get_precision('Account'),
            store={
                'hr.expense.expense': (lambda self, cr, uid, ids, c={}: ids,
                                       None, 50),
                'account.invoice': (_get_exp_from_invoice, None, 50)
            }),
        'advance_ids': fields.many2many(
            'account.move.line', 'expense_advance_rel',
            'expense_id', 'aml_id', string='Employee Advances',
            help="Advances associated to the expense employee."),
        'payment_status': fields.function(
            _get_payment_status, type='boolean',
            string = 'Expense Payment Status',
            store = {
                _inherit: (lambda self, c, u, ids, cx: ids, ['aml_ids'], 50)
            },),



        'aml_ids': fields.function(
            _her_entries, type='one2many', obj='account.move.line',
            string='Expense Journal Entry Lines'),
        'payment_ids': fields.many2many(
            'account.voucher', 'expense_pay_rel', 'expense_id', 'av_id',
            string=_('Expense Payments'),
            help=_('This table is a summary of the payments done to reconcile '
                   'the expense invoices, lines and advances. This is an only '
                   'read field that is set up once the expence reconciliation '
                   'is done (when user click the Reconcile button at the '
                   'Waiting Payment expense state.')),
        'skip': fields.boolean(
            string='This expense has not advances',
            help=_('Active this checkbox to allow leave the expense without '
                   'advances (This will create write off a journal entry when '
                   'reconciling). If this is not what you want please create '
                   'and advance for the expense employee and use the Refresh '
                   'button to associated to this expense')),
        'ait_ids': fields.function(
            _get_ait_ids,
            type="one2many",
            relation='account.invoice.tax',
            string=_('Deductible Tax Lines'),
            help=_('This are the account invoice taxes loaded into the '
                   'Expense invoices. The user can\'t change its content and '
                   'not have to worry about to fill the field. This taxes '
                   'will be auto update when the expense invoices change.\n\n'
                   'This invoices changes includes:\n - when a tax is added '
                   'or removed from an invoice line,\n - when an invoice line '
                   'is deleted from an invoice,\n - when the invoice is '
                   'unlinked to the expense.')),
        'state': fields.selection([
            ('draft', 'New'),
            ('cancelled', 'Refused'),
            ('confirm', 'Waiting Approval'),
            ('accepted', 'Approved'),
            ('done', 'Waiting Payment'),
            ('process', 'Processing Payment'),
            ('deduction', 'Processing Deduction'),
            ('paid', 'Paid')],
            'Status', readonly=True, track_visibility='onchange',
            help=_(
            'When the expense request is created the status is '
            '\'Draft\'.\n It is confirmed by the user and request is sent to '
            'admin, the status is \'Waiting Confirmation\'. \nIf the admin '
            'accepts it, the status is \'Accepted\'.\n If the accounting '
            'entries are made for the expense request, the status is '
            '\'Waiting Payment\'.')),
        'account_analytic_id': fields.many2one(
            'account.analytic.account',
            'Analytic'),
        'date_post': fields.date('Accounting Date')
    }

    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        res = super(HrExpenseExpense, self).onchange_employee_id(
            cr, uid, ids, employee_id, context=context)
        if not employee_id:
            return res

        emp_obj = self.pool.get('hr.employee')
        employee = emp_obj.browse(cr, uid, employee_id, context=context)
        acc_analytic_id = employee.account_analytic_id and\
            employee.account_analytic_id.id or False
        if not acc_analytic_id:
            acc_analytic_id = employee.department_id and\
                employee.department_id.analytic_account_id and\
                employee.department_id.analytic_account_id.id or False
        res['value'].update({'account_analytic_id': acc_analytic_id})
        return res

    def onchange_department_id(self, cr, uid, ids, employee_id, department_id,
                               context=None):
        dep_obj = self.pool.get('hr.department')
        emp_obj = self.pool.get('hr.employee')
        employee = emp_obj.browse(cr, uid, employee_id, context=context)
        acc_analytic_id = employee.account_analytic_id and\
            employee.account_analytic_id.id or False
        if not acc_analytic_id:
            acc_analytic_id = employee.department_id and\
                employee.department_id.analytic_account_id\
                and employee.department_id.analytic_account_id.id or False

        if not acc_analytic_id and department_id:
            department = dep_obj.browse(cr, uid, department_id,
                                        context=context)
            acc_analytic_id = department.analytic_account_id and \
                department.analytic_account_id.id or False
        res = {'value': {'account_analytic_id': acc_analytic_id}}
        return res

    def onchange_no_danvace_option(self, cr, uid, ids, skip, context=None):
        """Clean up the expense advances when the No advances checkbox is set
        """
        context = context or {}
        res = {'value': {}}
        if skip:
            res['value'] = {'advance_ids': []}
        else:
            self.load_advances(cr, uid, ids, context=context)
            if ids:
                res['value'] = {
                    'advance_ids':
                    [advn.id for advn in self.browse(
                     cr, uid, ids[0], context=context).advance_ids]
                }
        return res

    def check_invoice(self, cr, uid, ids, context=None):
        """ Verifying that all invoices related to this expense
        have been validated"""
        context = context or {}
        inv_brws = self.browse(cr, uid, ids[0], context=context).invoice_ids
        res = [True]
        if inv_brws:
            res += [inv.state == 'open' and True or False for inv in inv_brws]
            res = all(res)
        if not res:
            raise osv.except_osv(
                _('Invalid Procedure'),
                _('Please, Complete the validation of the remaining Draft '
                  'Invoices before continuing'))
        return True

    def expense_confirm(self, cr, uid, ids, context=None):
        """ Overwrite the expense_confirm method to validate that the expense
        have expenses lines before sending to Manager."""
        context = context or {}
        for exp in self.browse(cr, uid, ids, context=context):
            if not exp.invoice_ids and not exp.line_ids:
                raise osv.except_osv(
                    _('Invalid Procedure'),
                    _('You have not Deductible or No Deductible lines loaded '
                      'into the expense'))
            super(HrExpenseExpense, self).expense_confirm(
                cr, uid, ids, context=context)
        return True

    def load_advances(self, cr, uid, ids, context=None):
        """ Load the expense advances table with the corresponding data. Adds
        account move lines that fulfill the following conditions:
            - Not reconciled.
            - Not partially reconciled.
            - Account associated of type payable.
            - That belongs to the expense employee or to the expense invoices
              partners.
        """
        context = context or {}
        aml_obj = self.pool.get('account.move.line')
        acc_payable_ids = self.pool.get('account.account').search(
            cr, uid, [('type', '=', 'payable')], context=context)
        for exp in self.browse(cr, uid, ids, context=context):
            partner_ids = [exp.employee_id.address_home_id.id]
            aml_ids = aml_obj.search(
                cr, uid,
                [('reconcile_id', '=', False),
                 ('reconcile_partial_id', '=', False),
                 ('account_id', 'in', acc_payable_ids),
                 ('partner_id', 'in', partner_ids),
                 ('debit', '>', 0.0),
                 ], context=context)
            vals = {}
            cr.execute(('SELECT aml_id FROM expense_advance_rel '
                        'WHERE expense_id != %s'), (exp.id,))
            already_use_aml = cr.fetchall()
            already_use_aml = [dat[0] for dat in already_use_aml]
            aml_ids = list(set(aml_ids) - set(already_use_aml))
            vals['advance_ids'] = \
                [(6, 0, aml_ids)]
            self.write(cr, uid, exp.id, vals, context=context)
        return True

    # note: This method is not currently used. Can be used when trying to
    # print the payment info with some partner and date order (need to be
    # check)
    def order_payments(self, cr, uid, ids, aml_ids, context=None):
        """ orders the payments lines by partner id. Recive only one id"""
        context = context or {}
        exp = self.browse(cr, uid, ids, context=context)
        order_partner = list(set(
            [(payment.partner_id.name, payment.partner_id.id, payment.id)
             for payment in exp.advance_ids]))
        order_partner.sort()
        order_payments = [item[-1] for item in order_partner]
        return order_payments

    def group_aml_inv_ids_by_partner(self, cr, uid, aml_inv_ids,
                                     context=None):
        """Return a list o with sub lists of invoice ids grouped for partners.
        @param aml_inv_ids: list of invoices account move lines ids to order.
        """
        context = context or {}
        aml_obj = self.pool.get('account.move.line')
        inv_by = dict()
        for line in aml_obj.browse(cr, uid, aml_inv_ids, context=context):
            inv_by[line.partner_id.id] = \
                inv_by.get(line.partner_id.id, False) and \
                inv_by[line.partner_id.id] + [line.id] or \
                [line.id]
        return inv_by.values()

    def payment_reconcile(self, cr, uid, ids, context=None):
        """ It reconcile the expense advance and expense invoice account move
        lines.
        """
        context = context or {}
        aml_obj = self.pool.get('account.move.line')
        per_obj = self.pool.get('account.period')
        for exp in self.browse(cr, uid, ids, context=context):
            self.check_advance_no_empty_condition(cr, uid, exp.id,
                                                  context=context)
            if not exp.account_move_id:
                raise osv.except_osv(
                    _('Warning Data Integrity Failure!!!'),
                    _('Journal Entry for this Expense has been previously '
                      'deleted, please cancel document and go through the '
                      'previous steps up to this current step to recreate it!'
                      ))

            # manage the expense move lines
            exp_aml_brws = exp.account_move_id and \
                [aml_brw
                 for aml_brw in exp.account_move_id.line_id
                 if aml_brw.account_id.type == 'payable'] or []

            advance_aml_brws = [aml_brw
                                for aml_brw in exp.advance_ids
                                if aml_brw.account_id.type == 'payable']

            inv_aml_brws = [aml_brw
                            for inv in exp.invoice_ids
                            for aml_brw in inv.move_id.line_id
                            if aml_brw.account_id.type == 'payable']

            for av_brw in exp.payment_ids:
                advance_aml_brws += \
                    [l for l in av_brw.move_ids
                     if l.account_id.type == "payable"
                     and not l.reconcile_id and not l.reconcile_partial_id]

            aml = {
                'exp':
                exp_aml_brws and [aml_brw.id for aml_brw in exp_aml_brws]
                or [],
                'advances': [aml_brw.id for aml_brw in advance_aml_brws],
                'invs': [aml_brw.id for aml_brw in inv_aml_brws],
                # self.group_aml_inv_ids_by_partner(
                # cr, uid, [aml_brw.id for aml_brw in inv_aml_brws],
                # context=context),
                'debit':
                sum([aml_brw.debit
                     for aml_brw in advance_aml_brws]),
                'credit':
                sum([aml_brw.credit
                     for aml_brw in exp_aml_brws + inv_aml_brws]),
                'exp_sum':
                sum([aml_brw.credit
                     for aml_brw in exp_aml_brws]),
                'inv_sum':
                sum([aml_brw.credit
                     for aml_brw in inv_aml_brws]),
                'invs_ids': [inv.id
                             for inv in exp.invoice_ids]
            }

            aml_amount = aml['debit'] - aml['credit']
            adjust_balance_to = aml_amount == 0.0 and 'liquidate' or \
                (aml_amount > 0.0 and 'debit') or 'credit'
            part_rec, ff, pp = [], [], []
            # create and reconcile invoice move lines
            full_rec = aml['invs'] and self.create_and_reconcile_invoice_lines(
                cr, uid, exp.id, aml['invs'],
                adjust_balance_to=adjust_balance_to, context=context) or []

            # change expense state
            if adjust_balance_to == 'debit':
                ff, pp = self.expense_reconcile_partial_deduction(
                    cr, uid, exp.id, aml, context=context)
                self.write(
                    cr, uid, exp.id,
                    {'state': 'paid'}, context=context)
            elif adjust_balance_to == 'credit':
                ff, pp = self.expense_reconcile_partial_payment(
                    cr, uid, exp.id, aml, context=context)
                self.write(
                    cr, uid, exp.id,
                    {'state': 'process'}, context=context)
            elif adjust_balance_to == 'liquidate':
                ff, pp = self.expense_reconcile_partial_deduction(
                    cr, uid, exp.id, aml, context=context)
                self.write(cr, uid, exp.id, {'state': 'paid'}, context=context)

            date_post = exp.date_post or fields.date.today()

            period_id = per_obj.find(cr, uid, dt=date_post)
            period_id = period_id and period_id[0]
            exp.write({'date_post': date_post})

            if not exp.account_move_id:
                raise osv.except_osv(
                    _('Warning Data Integrity Failure!!!'),
                    _('Journal Entry for this Expense has been previously '
                      'deleted, please cancel document and go through the '
                      'previous steps up to this current step to recreate it!'
                      ))

            x_aml_ids = [aml_brw.id for aml_brw in exp.account_move_id.line_id]

            vals = {'date': date_post, 'period_id': period_id}
            exp.account_move_id.write(vals)
            aml_obj.write(cr, uid, x_aml_ids, vals)
            for line_pair in full_rec + [ff]:
                if not line_pair:
                    continue
                try:
                    aml_obj.reconcile(
                        cr, uid, line_pair, 'manual', context=context)
                except BaseException:
                    new_line_pair = self.invoice_counter_move_lines(
                        cr, uid, exp.id, am_id=exp.account_move_id.id,
                        aml_ids=line_pair,
                        context=context)
                    for nlp in new_line_pair:
                        aml_obj.reconcile(
                            cr, uid, nlp, 'manual', context=context)
            for line_pair in part_rec + [pp]:
                if not line_pair:
                    continue
                aml_obj.reconcile_partial(
                    cr, uid, line_pair, 'manual', context=context)
        return aml

    def expense_reconcile_partial_deduction(self, cr, uid, ids, aml,
                                            context=None):
        """This method make a distribution of the advances, whenever applies
        paying fully those invoice that can be paid and leaving just a
        remaining to that that just can be paid partially, this way is less
        cumbersome due to the fact that partial reconciliation in openerp over
        several invoice can be really __nasty__
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        exp = self.browse(cr, uid, ids[0], context=context)

        adv_ids = aml['advances']
        exp_ids = aml['exp']

        sum_adv = aml['debit']
        sum_inv = aml['inv_sum']

        ld = sum_adv - aml['credit']  # Remaining Advance
        if ld:
            self.expense_debit_lines(
                cr, uid, exp.id, exp.account_move_id.id, ld)
        lc = sum_adv - aml['credit'] + sum_inv
        lc = self.expense_credit_lines(
            cr, uid, exp.id, exp.account_move_id.id, lc)

        return adv_ids + exp_ids + [lc], []

    # pylint: disable=R0911
    def expense_reconcile_partial_payment(self, cr, uid, ids, aml,
                                          context=None):
        """This method make a distribution of the advances, whenever applies
        paying fully those invoice that can be paid and leaving just a
        remaining to that that just can be paid partially, this way is less
        cumbersome due to the fact that partial reconciliation in openerp over
        several invoice can be really __nasty__
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        exp = self.browse(cr, uid, ids[0], context=context)

        adv_ids = aml['advances']
        exp_ids = aml['exp']

        sum_adv = aml['debit']
        sum_exp = aml['exp_sum']
        sum_inv = aml['inv_sum']
        partial_rec = []
        full_rec = []

        if not sum_adv and sum_inv:
            inv_ids = [self.expense_credit_lines(
                       cr, uid, exp.id, exp.account_move_id.id, sum_inv)]
            return full_rec, partial_rec
        elif sum_exp < sum_adv:  # and sum_inv > 0
            l1 = sum_adv - sum_exp
            l2 = sum_inv - l1
            l1 = self.expense_credit_lines(
                cr, uid, exp.id, exp.account_move_id.id, l1)
            l2 = self.expense_credit_lines(
                cr, uid, exp.id, exp.account_move_id.id, l2)
            return [l1] + adv_ids + exp_ids, []
        elif sum_exp == sum_adv:
            return adv_ids + exp_ids, []
        else:  # sum_exp > sum_adv
            inv_ids = [self.expense_credit_lines(
                cr, uid, exp.id, exp.account_move_id.id, sum_inv)]
            if sum_adv > sum_inv:
                return [], exp_ids + adv_ids
            elif sum_adv == sum_inv:
                return adv_ids + inv_ids, []
            else:  # sum_adv < sum_inv
                return [], adv_ids + inv_ids
        return [], []

    def expense_debit_lines(self, cr, uid, ids, am_id, amount,
                            account_id=False, partner_id=False, date=None,
                            advance_amount=False, line_type=None,
                            adjust_balance_to=None, context=None):
        """Create new move lines to match to the expense. receive only one id
        @param aml_ids: acc.move.line list of ids
        @param am_id: account move id
        """
        context = context or {}
        aml_obj = self.pool.get('account.move.line')
        exp = self.browse(cr, uid, ids, context=context)
        account_id = account_id or exp.employee_id.address_home_id and\
            exp.employee_id.address_home_id.property_account_payable.id
        partner_id = partner_id or exp.employee_id.address_home_id and \
            exp.employee_id.address_home_id.id
        vals = {
            'move_id': am_id,
            'journal_id': exp.account_move_id.journal_id.id,
            'date': date or fields.date.today(),
            'period_id': self.pool.get('account.period').find(
                cr, uid, context=context)[0],
            'debit': amount,
            'name': _('Remaining Employee Advance'),
            'partner_id': partner_id,
            'account_id': account_id,
            'credit': 0.0,
        }
        return aml_obj.create(cr, uid, vals, context=context)

    def expense_credit_lines(self, cr, uid, ids, am_id, amount,
                             account_id=False, partner_id=False, date=None,
                             advance_amount=False, line_type=None,
                             adjust_balance_to=None, context=None):
        """Create new move lines to match to the expense. receive only one id
        @param aml_ids: acc.move.line list of ids
        @param am_id: account move id
        """
        context = context or {}
        aml_obj = self.pool.get('account.move.line')
        exp = self.browse(cr, uid, ids, context=context)
        account_id = account_id or exp.employee_id.address_home_id and\
            exp.employee_id.address_home_id.property_account_payable.id
        partner_id = partner_id or exp.employee_id.address_home_id and \
            exp.employee_id.address_home_id.id

        if not exp.account_move_id:
            raise osv.except_osv(
                _('Warning Data Integrity Failure!!!'),
                _('Journal Entry for this Expense has been previously '
                  'deleted, please cancel document and go through the '
                  'previous steps up to this current step to recreate it!'
                  ))

        vals = {
            'move_id': am_id,
            'journal_id': exp.account_move_id.journal_id.id,
            'date': date or fields.date.today(),
            'period_id': self.pool.get('account.period').find(
                cr, uid, context=context)[0],
            'debit': 0.0,
            'name': _('Debts to be reimbursed to Employee'),
            'partner_id': partner_id,
            'account_id': account_id,
            'credit': amount,
        }
        return aml_obj.create(cr, uid, vals, context=context)

    def expense_reconcile_partial(self, cr, uid, ids, context=None):
        """make a partial reconciliation between invoices debit and advances
        credit.
        """
        context = context or {}
        aml_obj = self.pool.get('account.move.line')
        ids = isinstance(ids, (int, long)) and [ids] or ids
        for exp in self.browse(cr, uid, ids, context=context):
            exp_debit_lines = [aml.id for aml in exp.advance_ids]
            exp_credit_lines = [aml.id
                                for aml in exp.account_move_id.line_id
                                if aml.credit > 0.0]
            aml_obj.reconcile_partial(
                cr, uid, exp_debit_lines + exp_credit_lines, 'manual',
                context=context)
        return True

    def expense_reconcile(self, cr, uid, ids, context=None):
        """When expense debit and credit are equal.
        """
        context = context or {}
        aml_obj = self.pool.get('account.move.line')
        ids = isinstance(ids, (int, long)) and [ids] or ids
        for exp in self.browse(cr, uid, ids, context=context):
            exp_debit_lines = [aml.id for aml in exp.advance_ids]
            exp_credit_lines = [aml.id
                                for aml in exp.account_move_id.line_id
                                if aml.credit > 0.0]
            aml_obj.reconcile(cr, uid, exp_debit_lines + exp_credit_lines,
                              'manual', context=context)
        return True

    def check_advance_no_empty_condition(self, cr, uid, ids, context=None):
        """Check if the Expense have not advances and force him to active the
        checkbox for allow leave the advances empty and leave the user now
        the repercussions of this configuration.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        for exp in self.browse(cr, uid, ids, context=context):
            if exp.advance_ids and not exp.skip:
                pass
            elif exp.advance_ids and exp.skip:
                raise osv.except_osv(
                    _('Invalid Procedure!'),
                    _('Integrity Problem. You have advances for this expense '
                      'but in same time you active the No advances option. '
                      'Please uncheck the No advances option or clean the '
                      'advances table instead.'))
            elif not exp.advance_ids and not exp.skip:
                raise osv.except_osv(
                    _('Invalid Procedure!'),
                    _('You have leave the expense advances empty (Renconcile '
                      'the Expense will cause a Write Off journal entry). If '
                      'this is your purpose its required to check the This '
                      'expense has not advances checkbox into the expense '
                      'advances page. If not, please create some advances for '
                      'the employee and Refresh the expense advance lines '
                      'with the expense advance page refresh button.'))
            elif not exp.advance_ids and exp.skip:
                # reconciling the expense withhout advances
                pass
        return True

    def create_and_reconcile_invoice_lines(self, cr, uid, ids, inv_aml_ids,
                                           adjust_balance_to, context=None):
        """Create the account move lines to balance the expense invoices and
        reconcile them with the original invoice move lines.
        @param inv_aml_ids: list of expense invoices move line ids.
        @param adjust_balance_to: indicates who is greater credit or debit.
        """
        context = context or {}

        ids = isinstance(ids, (int, long)) and [ids] or ids
        for exp in self.browse(cr, uid, ids, context=context):
            # create invoice move lines.
            inv_match_pair = self.invoice_counter_move_lines(
                cr, uid, exp.id,
                am_id=exp.account_move_id.id,
                aml_ids=inv_aml_ids,
                context=context)
        return inv_match_pair

    def invoice_counter_move_lines(self, cr, uid, ids, am_id, aml_ids,
                                   advance_amount=False, line_type=None,
                                   adjust_balance_to=None, context=None):
        """Create new move lines to match to the expense. receive only one id
        @param aml_ids: acc.move.line list of ids
        @param am_id: account move id
        """
        context = context or {}
        res = []
        aml_obj = self.pool.get('account.move.line')
        exp = self.browse(cr, uid, ids, context=context)
        vals = {
            'move_id': am_id,
            'journal_id': exp.journal_id and exp.journal_id.id or False,
            'date': fields.date.today(),
            'period_id': self.pool.get('account.period').find(
                cr, uid, context=context)[0],
            'name': _('Payment through Expense'),
        }

        for aml_brw in aml_obj.browse(cr, uid, aml_ids, context=context):
            vals_debit = vals.copy()
            vals_debit['partner_id'] = aml_brw.partner_id.id
            vals_debit['account_id'] = aml_brw.account_id.id
            vals_debit['debit'] = aml_brw.credit
            vals_debit['credit'] = aml_brw.debit

            debit_id = aml_obj.create(cr, uid, vals_debit, context=context)
            res.append([aml_brw.id, debit_id])
        return res

    def create_reconcile_move_lines(self, cr, uid, ids, am_id, aml_ids,
                                    advance_amount=False, line_type=None,
                                    adjust_balance_to=None, context=None):
        """Create new move lines to match to the expense. receive only one id
        @param aml_ids: acc.move.line list of ids
        @param am_id: account move id
        """
        context = context or {}
        res = []
        aml_obj = self.pool.get('account.move.line')
        exp = self.browse(cr, uid, ids, context=context)
        vals = {}.fromkeys(['partner_id', 'debit', 'credit',
                            'name', 'move_id', 'account_id'])
        vals['move_id'] = am_id
        no_advance_account = \
            exp.employee_id.address_home_id.property_account_payable.id
        vals['journal_id'] = exp.journal_id
        vals['period_id'] = self.pool.get('account.period').find(
            cr, uid, context=context)[0]
        vals['date'] = time.strftime('%Y-%m-%d')

        advance_name = {
            'debit_line':
            adjust_balance_to == 'debit' and _('(Remaining Advance)')
            or _('(Reconciliation)'),

            'credit_line':
            adjust_balance_to == 'debit' and _('(Applyed Advance)')
            or _('(Debt to employee)'),
        }

        for aml_id in aml_ids:
            aml_brw = aml_id \
                and aml_obj.browse(cr, uid, aml_id, context=context) \
                or False
            # DEBIT LINE
            debit_vals = vals.copy()
            debit_vals.update({
                'partner_id': line_type == 'advance' and
                exp.employee_id.address_home_id.id or
                aml_brw.partner_id.id,

                'debit':
                line_type == 'advance' and advance_amount or
                aml_brw.credit,

                'credit': 0.0,

                'name':
                line_type == 'invoice' and _('Payable to Partner')
                    or _('Payable to Employee') +
                    (line_type == 'advance' and ' ' +
                        advance_name['debit_line'] or ''),

                'account_id':
                aml_brw and aml_brw.account_id.id
                or adjust_balance_to in ['no-advance']
                and no_advance_account or False,
            })
            debit_id = aml_obj.create(cr, uid, debit_vals, context=context)
            # CREDIT LINE
            credit_vals = vals.copy()
            credit_vals.update({
                'partner_id': exp.employee_id.address_home_id.id,
                'debit': 0.0,
                'credit':
                line_type == 'advance' and advance_amount
                or aml_brw.credit,

                'name':
                _('Payable to Employee') + (line_type == 'advance' and ' ' +
                                            advance_name['credit_line'] or ''),

                'account_id':
                aml_brw and aml_brw.account_id.id
                or adjust_balance_to in ['no-advance']
                and no_advance_account or False,
            })
            credit_id = aml_obj.create(cr, uid, credit_vals, context=context)

            if line_type in ['invoice']:
                res.append((aml_brw.id, debit_id))
            elif line_type in ['advance']:
                match_id = adjust_balance_to == 'debit' and credit_id \
                    or debit_id
                res.extend([aml_brw.id, match_id])
        return res

    def check_expense_invoices(self, cr, uid, ids, context=None):
        """ Overwrite the expense_accept method to add the validate
        invoice process """
        context = context or {}
        error_msj = str()
        for exp_brw in self.browse(cr, uid, ids, context=context):
            bad_invs = [inv_brw
                        for inv_brw in exp_brw.invoice_ids
                        if inv_brw.state not in ['open']]

            if bad_invs:
                for inv_brw in bad_invs:
                    error_msj = error_msj + \
                        '- ' + (inv_brw.number or inv_brw.partner_id.name) + \
                        ' Invoice total ' + str(inv_brw.amount_total) + ' (' \
                        + inv_brw.state.capitalize() + ')\n'

        if error_msj:
            raise osv.except_osv(
                _('Invalid Procedure'),
                _('The expense invoices need to be validated. After manually '
                  'check invoices you can validate all invoices in batch by '
                  'using the Validate Invoices button. \n Invoices to '
                  'Validate:\n')
                + error_msj)
        return True

    def validate_expense_invoices(self, cr, uid, ids, context=None):
        """ Validate Invoices asociated to the Expense. Put the invoices in
        Open State. """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wf_service = workflow
        inv_obj = self.pool.get('account.invoice')
        for exp_brw in self.browse(cr, uid, ids, context=context):
            self.check_inv_periods(cr, uid, exp_brw.id, context=context)
            validate_inv_ids = \
                [inv_brw.id
                 for inv_brw in exp_brw.invoice_ids
                 if inv_brw.state == 'draft']
            inv_obj.write(cr, uid, validate_inv_ids, {
                'date_invoice': exp_brw.date_post,
                'period_id': False,
            }, context=context)
            for inv_id in validate_inv_ids:
                wf_service.trg_validate(uid, 'account.invoice', inv_id,
                                        'invoice_open', cr)
        return True

    def check_inv_periods(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        exp_brw = self.browse(cr, uid, ids[0], context=context)
        period_obj = self.pool.get('account.period')
        res = []
        for inv_brw in exp_brw.invoice_ids:
            if inv_brw.state == 'draft':
                pass
            elif inv_brw.state in ('cancel', 'paid'):
                res.append(inv_brw)
            elif inv_brw.state == 'open':
                if inv_brw.payment_ids:
                    res.append(inv_brw)
                elif [inv_brw.period_id.id] != period_obj.find(
                        cr, uid, dt=exp_brw.date_post):
                    res.append(inv_brw)
        if res:
            note = \
                _('The folliwing invoices cannot be used in this Expense:\n')
            for inv_brw in res:
                note += '%s - %s -%s - %s \n' % \
                    (inv_brw.supplier_invoice_number, inv_brw.partner_id.name,
                     inv_brw.date_invoice, inv_brw.period_id.name)
            raise osv.except_osv(_('Error!'), note)
        return True

    # note: This method is not used. Can be used when the validating invoice
    # process its automatize when generating accounting entries (it works).
    def generate_accounting_entries(self, cr, uid, ids, context=None):
        """ Active the workflow signals to change the expense to Done state
        and generate accounting entries for the expense by clicking the
        'Generate Accounting Entries' button. """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wf_service = workflow
        for exp_brw in self.browse(cr, uid, ids, context=context):
            if exp_brw.state not in ['done']:
                wf_service.trg_validate(uid, 'hr.expense.expense', exp_brw.id,
                                        'confirm', cr)
                wf_service.trg_validate(uid, 'hr.expense.expense', exp_brw.id,
                                        'validate', cr)
                wf_service.trg_validate(uid, 'hr.expense.expense', exp_brw.id,
                                        'done', cr)
        return True

    def expense_pay(self, cr, uid, ids, context=None):
        """Expense credit is greater than the expense debit. That means that the
        expense have no advances or the total advances amount dont fullfill the
        payment. So now we create a account voucher to pay the employee the
        missing expense amount.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        if not ids:
            return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(
            cr, uid,
            'hr_expense_replenishment', 'view_vendor_receipt_dialog_form')
        exp_brw = self.browse(cr, uid, ids[0], context=context)
        return {
            'name': _("Pay Employee Expense"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'payment_expected_currency': exp_brw.currency_id.id,
                'default_partner_id': exp_brw.partner_id.id,
                'default_amount': exp_brw.amount,
                'default_name': exp_brw.name,
                'default_reference': '',
                'close_after_process': True,
                'default_type': 'payment',
                'type': 'payment',
                'employee_payment': True,
            }
        }

    def expense_deduction(self, cr, uid, ids, context=None):
        """Expense debit is greater than the expense credit. That means that the
        expense have advances and they fullfill the payment. So now is time
        to reconcile expense payable move lines with the expense advances.
        """
        context = context or {}
        aml_obj = self.pool.get('account.move.line')
        for exp in self.browse(cr, uid, ids, context=context):
            debit = sum([aml.debit for aml in exp.advance_ids])
            credit = sum([aml.credit
                          for aml in exp.account_move_id.line_id
                          if aml.credit > 0.0])
            credit_aml_ids = [aml.id
                              for aml in exp.account_move_id.line_id
                              if aml.credit > 0.0]
            debit_aml_ids = [aml.id for aml in exp.advance_ids]
            advance_match_pair = \
                self.create_reconcile_move_lines(
                    cr, uid, exp.id,
                    am_id=exp.account_move_id.id,
                    aml_ids=debit_aml_ids,
                    advance_amount=debit - credit,
                    line_type='advance',
                    adjust_balance_to='debit',
                    context=context)
            reconcile_list = advance_match_pair + credit_aml_ids
            aml_obj.reconcile(cr, uid, reconcile_list, 'manual',
                              context=context)
            self.write(cr, uid, exp.id, {'state': 'paid'}, context=context)
        return True

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'advance_ids': [],
                        'invoice_ids': [],
                        'payment_ids': [],
                        'ail_ids': [],
                        'ait_ids': [],
                        'date_post': False,
                        })
        return super(HrExpenseExpense, self).copy(default)

    def show_entries(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = self.her_entries(cr, uid, ids, context=context)

        return {
            'domain': "[('id','in',\
                [" + ','.join([str(res_id) for res_id in res[ids[0]]]) + "])]",
            'name': _('Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }

    def print_journal_entries(self, cr, uid, ids, context=None):
        account_move_ids = []
        for exp in self.browse(cr, uid, ids, context=context):
            res_exp = [move.move_id.id for move in exp.account_move_id.line_id]

            res_adv = [line.move_id.id for line in exp.advance_ids]

            res_pay = [line2.move_id.id for pay in exp.payment_ids
                       for line2 in pay.move_ids]

            res_inv = [move2.move_id.id for inv in exp.invoice_ids
                       for move2 in inv.move_id.line_id]

        account_move_ids = res_exp + res_adv + res_pay + res_inv
        if account_move_ids:
            datas = {'ids': list(set(account_move_ids))}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.move.report.webkit',
            'datas': datas
        }

    def action_receipt_create(self, cr, uid, ids, context=None):
        """main function that is called when trying to create the accounting
        entries related to an expense then this super tries to get rid of
        the Journal Entry Lines in zero
        """
        super(HrExpenseExpense, self).action_receipt_create(
            cr, uid, ids, context=context)
        aml_obj = self.pool.get('account.move.line')
        res = []
        for exp in self.browse(cr, uid, ids, context=context):
            if not exp.account_move_id.journal_id.entry_posted:
                for aml_brw in exp.account_move_id.line_id:
                    if not aml_brw.debit and not aml_brw.credit:
                        res.append(aml_brw.id)
        if res:
            aml_obj.unlink(cr, uid, res, context=context)
        return True

    def account_move_get(self, cr, uid, expense_id, context=None):
        """This method prepare the creation of the account move related to the
        given expense.

        For this case it will override the date_confirm using date_post

        :param expense_id: Id of voucher for which we are creating
                           account_move.
        :return: mapping between fieldname and value of account move to create
        :rtype: dict
        """
        context = context or {}
        period_obj = self.pool.get('account.period')
        expense = self.browse(cr, uid, expense_id, context=context)
        date = expense.date_post
        res = super(HrExpenseExpense, self).account_move_get(
            cr, uid, expense_id, context=context)
        res.update({
            'date': date,
            'period_id': period_obj.find(cr, uid, date, context=context)[0],
        })
        return res


class AccountVoucher(osv.Model):
    _inherit = 'account.voucher'

    def create(self, cr, uid, vals, context=None):
        context = context or {}
        res = super(AccountVoucher, self).create(
            cr, uid, vals, context=context)
        if context.get('employee_payment', False):
            exp_obj = self.pool.get('hr.expense.expense')
            exp_obj.write(cr, uid, context['active_id'], {
                'payment_ids': [(4, res)]
            }, context=context)
        return res


class AccountMoveLine(osv.osv):
    _inherit = "account.move.line"

    # pylint: disable=W0622
    def reconcile(self, cr, uid, ids, type='auto', writeoff_acc_id=False,
                  writeoff_period_id=False, writeoff_journal_id=False,
                  context=None):
        res = super(AccountMoveLine, self).reconcile(
            cr, uid, ids, type=type, writeoff_acc_id=writeoff_acc_id,
            writeoff_period_id=writeoff_period_id,
            writeoff_journal_id=writeoff_journal_id,
            context=context)

        account_move_ids = [aml.move_id.id for aml in self.browse(
            cr, uid, ids, context=context)]
        expense_obj = self.pool.get('hr.expense.expense')
        currency_obj = self.pool.get('res.currency')
        if account_move_ids:
            expense_ids = expense_obj.search(
                cr, uid,
                [('account_move_id', 'in', account_move_ids)], context=context)
            for expense in expense_obj.browse(cr, uid, expense_ids,
                                              context=context):
                if expense.state in ('process', 'deduction'):
                    new_status_is_paid = True
                    for aml in expense.account_move_id.line_id:
                        if aml.account_id.type == 'payable' and not\
                            currency_obj.is_zero(
                                cr,
                                uid,
                                expense.company_id.currency_id,
                                aml.amount_residual):
                            new_status_is_paid = False
                    if new_status_is_paid:
                        expense_obj.write(cr, uid, [expense.id],
                                          {'state': 'paid'}, context=context)
        return res


class HrEmployee(osv.Model):
    _inherit = 'hr.employee'

    _columns = {
        'account_analytic_id': fields.many2one(
            'account.analytic.account',
            'Analytic', domain=[('type', '<>', 'view')])
    }


class HrDepartment(osv.Model):
    _inherit = "hr.department"

    _columns = {
        'analytic_account_id': fields.many2one(
            'account.analytic.account',
            'Analytic', domain=[('type', '<>', 'view')]),
    }


class HrExpenseLine(osv.Model):
    _inherit = "hr.expense.line"

    def _get_analytic(self, cr, uid, context=None):
        context = context or {}
        res = super(HrExpenseLine, self)._get_analytic(
            cr, uid, context=context)
        result = context.get('account_analytic_exp', res)
        return result

    _defaults = {
        'analytic_account': _get_analytic
    }
