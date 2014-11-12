#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral          <kathy@vauxoo.com>
#    Planified by: Humberto Arocha       <hbto@vauxoo.com>
#    Audited by: Humberto Arocha         <hbto@vauxoo.com>
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
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp


class hr_expense_expense(osv.Model):
    _inherit = "hr.expense.expense"
    _columns = {
        'fully_applied_vat': fields.boolean('Fully Applied VAT',
                help=('Indicates if VAT has been computed in this expense')),
        'amount_exp_pay': fields.float('Amount Tax Pay',
                                    digits_compute=dp.get_precision('Account'))
    }

    def copy(self, cr, uid, ids, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'fully_applied_vat': False,
                        })
        return super(hr_expense_expense, self).copy(cr, uid, ids, default,
                        context=context)

    def payment_reconcile(self, cr, uid, ids, context=None):
        """ It reconcile the expense advance and expense invoice account move
        lines.
        """
        context = context or {}
        res = super(hr_expense_expense, self).payment_reconcile(cr, uid, ids,
                                                            context=context)
        self.create_her_tax_pay_adv(cr, uid, ids, context=context)
        return res

    def create_her_tax_pay_adv(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        for exp in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, ids, {'amount_exp_pay': 0.0})
            self.unlink_move_tax(cr, uid, exp, context=context)
            self.create_her_tax(cr, uid, exp.id, aml={}, context=context)
            for voucher_brw in exp.payment_ids:
                if voucher_brw.state == 'posted':
                    context.update({'payment_amount': voucher_brw.amount,
                                    'date_voucher': voucher_brw.date})
                    self.create_her_tax(cr, uid, exp.id, aml={}, context=context)
            self.apply_round_tax(cr, uid, exp.id, context=context)
        return True

    def create_her_tax(self, cr, uid, ids, aml=None, context=None):
        aml_obj = self.pool.get('account.move.line')
        acc_voucher_obj = self.pool.get('account.voucher')
        context = context or {}
        if aml is None:
            aml = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        exp = self.browse(cr, uid, ids, context=context)[0]

        company_currency = self._get_company_currency(cr, uid,
                            exp.id, context)

        current_currency = self._get_current_currency(cr, uid,
                            exp.id, context)

#        if exp.fully_applied_vat:
 #           return True
   #     self.unlink_move_tax(cr, uid, exp, context=context)
        expense_amount = sum([inv.amount_total for inv in exp.invoice_ids])
        if context.get('payment_amount'):
            advance_amount = context.get('payment_amount', 0.0)
            move_date = context.get('date_voucher', False)
        else:
            advance_amount = sum([adv.debit for adv in exp.advance_ids])
            if advance_amount > expense_amount:
                advance_amount = expense_amount
            move_date = exp.account_move_id.date

        if (exp.amount_exp_pay + advance_amount) > expense_amount:
            advance_amount = expense_amount - exp.amount_exp_pay
            if advance_amount == 0.0:
                return True

        percent_pay = expense_amount and advance_amount / expense_amount or 1

#        amount_tax_inv = sum( [invoice.amount_tax for invoice in exp.invoice_ids] )
 #
  #      amount_tax_pay = sum( [move_line_tax.debit for move_line_tax in\
   #                             aml_obj.browse(cr, uid,
    #                            self.move_tax_expense(cr, uid, exp, context=context))] )

#        print amount_tax_inv,'amount_tax_invamount_tax_inv'
 #       print amount_tax_pay,'amount_tax_payamount_tax_payamount_tax_pay'
  #
   #    if amount_tax_inv > amount_tax_pay:

        for invoice in exp.invoice_ids:
            for tax in invoice.tax_line:
                if tax.tax_id.tax_voucher_ok:
                    account_tax_voucher = tax.tax_id.account_paid_voucher_id.id
                    account_tax_collected = tax.tax_id.account_collected_id.id
                    factor = acc_voucher_obj.get_percent_pay_vs_invoice(cr, uid,
                        tax.amount * percent_pay, tax.amount * percent_pay,
                        context=context)
                    move_lines_tax = acc_voucher_obj.\
                        _preparate_move_line_tax(cr, uid,
                        account_tax_voucher,
                        account_tax_collected, exp.account_move_id.id,
                        'payment', invoice.partner_id.id,
                        exp.account_move_id.period_id.id,
                        exp.account_move_id.journal_id.id,
                        move_date, company_currency,
                        tax.amount * percent_pay, tax.amount * percent_pay,
                        current_currency,
                        False, tax.tax_id, tax.account_analytic_id and
                            tax.account_analytic_id.id or False,
                        tax.base_amount, factor, context=context)

                    for move_line_tax in move_lines_tax:
                        aml_obj.create(cr, uid, move_line_tax,
                                                context=context)

        self.write(cr, uid, ids,
                   {'amount_exp_pay': exp.amount_exp_pay + advance_amount})
#        exp.write({'fully_applied_vat':True})
        return True

    def _get_company_currency(self, cr, uid, exp_id, context=None):
        return self.pool.get('hr.expense.expense').browse(cr,
            uid, exp_id,
            context).account_move_id.journal_id.company_id.currency_id.id

    def _get_current_currency(self, cr, uid, exp_id, context=None):
        exp = self.pool.get('hr.expense.expense').browse(cr, uid, exp_id,
                                                         context)
        return exp.currency_id.id or\
            self._get_company_currency(cr, uid, exp_id, context)

    def move_tax_expense(self, cr, uid, exp, context=None):
        aml_obj = self.pool.get('account.move.line')
        acc_tax_v = []
        acc_tax_c = []
        for invoice in exp.invoice_ids:
            for tax in invoice.tax_line:
                if tax.tax_id.tax_voucher_ok:
                    acc_tax_v.append(tax.tax_id.account_paid_voucher_id.id)
                    acc_tax_c.append(tax.tax_id.account_collected_id.id)
        acc_inv_tax = list(set(acc_tax_v + acc_tax_c))
        move_tax_ids = aml_obj.search(cr, uid, [
            ('move_id', '=', exp.account_move_id.id),
            ('account_id', 'in', (acc_inv_tax))
        ])
        return move_tax_ids

    def unlink_move_tax(self, cr, uid, exp, context=None):
        if context in None:
            context = {}
        aml_obj = self.pool.get('account.move.line')
        move_ids = self.move_tax_expense(cr, uid, exp, context=context)
        aml_obj.unlink(cr, uid, move_ids)
        return True

    def apply_round_tax(self, cr, uid, ids, context=None):
        aml_obj = self.pool.get('account.move.line')
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        for exp in self.browse(cr, uid, ids, context=context):
            move_ids = self.move_tax_expense(cr, uid, exp, context=context)
            move_round = 0
            move_without_round = 0
            for move in aml_obj.browse(cr, uid, move_ids, context=context):
                if move.amount_tax_unround:
                    move_round += move.credit
                    move_without_round += abs(move.amount_tax_unround)
            move_diff = abs(move_without_round) - abs(move_round)
            move_diff = round(move_diff, 2)
            if move_diff != 0.00:
                move_ids.sort()
                for move_line in aml_obj.browse(cr, uid, move_ids[-2:],
                                                context=context):
                    if move_line.credit == 0 and move_line.debit:
                        cr.execute('UPDATE account_move_line '
                                   'SET debit=%s WHERE id=%s ',
                        (move_line.debit + move_diff, move_line.id))

                    if move_line.debit == 0 and move_line.credit:
                        cr.execute('UPDATE account_move_line '
                                   'SET credit=%s WHERE id=%s ',
                        (move_line.credit + move_diff, move_line.id))
        return True


class account_voucher(osv.Model):
    _inherit = 'account.voucher'

    def proforma_voucher(self, cr, uid, ids, context=None):
        context = context or {}
        hr_expense_obj = self.pool.get('hr.expense.expense')
        account_voucher_obj = self.pool.get('account.voucher')
        cr.execute("select * from expense_pay_rel where av_id = %s", (ids[0], ))
        dat = cr.dictfetchall()
        if dat:
            voucher_brw = account_voucher_obj.browse(cr, uid, dat[0]['av_id'],
                                            context=context)
            context.update({'payment_amount': voucher_brw.amount,
                            'date_voucher': voucher_brw.date})
            hr_expense_obj.create_her_tax(cr, uid, dat[0]['expense_id'], aml={},
                                        context=context)
        return super(account_voucher,
                     self).proforma_voucher(cr, uid, ids, context=context)


class account_move_line(osv.osv):
    _inherit = "account.move.line"

    def reconcile(self, cr, uid, ids, type='auto', writeoff_acc_id=False,
                  writeoff_period_id=False, writeoff_journal_id=False,
                  context=None):
        account_move_ids = [aml.move_id.id for aml in self.browse(cr, uid, ids,
            context=context)]
        expense_obj = self.pool.get('hr.expense.expense')
        if account_move_ids:
            expense_ids = expense_obj.search(cr, uid,
                [('account_move_id', 'in', account_move_ids)], context=context)
            for expense in expense_obj.browse(cr, uid, expense_ids,
                                              context=context):
                context['apply_round'] = True
                res = super(account_move_line, self).reconcile(cr, uid, ids,
                                    type=type,
                                    writeoff_acc_id=writeoff_acc_id,
                                    writeoff_period_id=writeoff_period_id,
                                    writeoff_journal_id=writeoff_journal_id,
                                    context=context)
                if expense.state == "paid":
                    expense_obj.apply_round_tax(cr, uid, expense.id,
                                                context=context)
                    expense_obj.write(cr, uid, expense.id,
                                      {'fully_applied_vat': True})
                return res
        return super(account_move_line, self).reconcile(cr, uid, ids,
                                    type=type,
                                    writeoff_acc_id=writeoff_acc_id,
                                    writeoff_period_id=writeoff_period_id,
                                    writeoff_journal_id=writeoff_journal_id,
                                    context=context)
