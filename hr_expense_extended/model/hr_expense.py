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
from openerp import netsvc
import openerp.addons.decimal_precision as dp


class hr_expense_expense(osv.Model):
    _inherit = "hr.expense.expense"

    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        """ Overwrite method to add the sum of the invoices total amount
        (Sub total + tax amount ). """
        context = context or {}
        res = super(hr_expense_expense, self)._amount(
            cr, uid, ids, field_name, arg, context=context)
        for expense in self.browse(cr, uid, res.keys(), context=context):
            for invoice in expense.invoice_ids:
                res[expense.id] += invoice.amount_total
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

    _columns = {
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
        'payment_ids': fields.many2many(
            'account.move.line','expense_payment_rel',
            'expense_id', 'aml_id', string='Payments',
            help="Payments associated to the expense."),
        'skip': fields.boolean(
            'Check this option if the expense has not advances')
    }

    def expense_accept(self, cr, uid, ids, context=None):
        """ Overwrite the expense_confirm function to add the validate
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
                        '- [Expense] ' + exp_brw.name + \
                        ' [Invoice] ' + (inv_brw.number or
                        inv_brw.partner_id.name) + \
                        ' (' + inv_brw.state.capitalize() + ')\n'

        if error_msj:
            raise osv.except_osv(
                'Invalid Procedure!',
                "Associated invoices need to be in Open state.\n"
                + error_msj)

        # create accounting entries related to an expense
        return super(hr_expense_expense, self).expense_accept(
            cr, uid, ids, context=context)

    def action_receipt_create(self, cr, uid, ids, context=None):
        """ overwirte the method to create expense accounting entries to
        add the first fill of the expense payments table """
        context = context or {}
        super(hr_expense_expense,self).action_receipt_create(
            cr, uid, ids, context=context)
        self.load_payments(cr, uid, ids, context=context)
        return True

    def load_payments(self, cr, uid, ids, context=None):
        """ Load the expense payment table with the corresponding data. Adds
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
            partner_ids = [inv.partner_id.id for inv in exp.invoice_ids]
            partner_ids.append(exp.account_move_id.partner_id.id)
            aml_ids = aml_obj.search(
                cr, uid,
                [('reconcile_id', '=', False),
                 ('reconcile_partial_id', '=', False),
                 ('account_id', 'in', acc_payable_ids),
                 ('partner_id', 'in', partner_ids)], context=context)
            vals = {}
            vals['payment_ids'] = \
                [(6, 0, aml_ids)]
            self.write(cr, uid, exp.id, vals, context=context)
        return True

    def order_payments(self, cr, uid, ids, aml_ids, context=None):
        """ orders the payments lines by partner id. Recive only one id"""
        context = context or {}
        aml_obj = self.pool.get('account.move.line')
        exp = self.browse(cr, uid, ids, context=context)
        order_partner = list(set(
            [(payment.partner_id.name, payment.partner_id.id, payment.id)
             for payment in exp.payment_ids]))
        order_partner.sort()
        order_payments = [item[-1] for item in order_partner]
        return order_payments

    #~ TODO: Doing
    def reconcile_viatical_payment(self, cr, uid, ids, context=None):
        """ It concile a new journal entry that englobs the expense accounting
        entry and the invoices accounting entries.
        """
        context = context or {}
        wf_service = netsvc.LocalService("workflow")
        aml_obj = self.pool.get('account.move.line')
        per_obj = self.pool.get('account.period')
        for exp_brw in self.browse(cr, uid, ids, context=context):
            # create move account
            exp_move_id = self.create_match_move(cr, uid, exp_brw.id,
                                                 context=context)
            print '\n'*5, 'exp_move_id', exp_move_id

            # reconcile manual entries for partners
            inv_move_ids = [inv_brw.move_id.id
                            for inv_brw in exp_brw.invoice_ids
                            if inv_brw.move_id]
            move_ids = [exp_move_id] + inv_move_ids
            move_line_ids = aml_obj.search(
                cr, uid, [('move_id', 'in', move_ids)], context=context)

            move_lines_ids_d = dict()
            for line in aml_obj.browse(
                    cr, uid, move_line_ids, context=context):
                if move_lines_ids_d.get(line.partner_id.id, False):
                    move_lines_ids_d[line.partner_id.id] += [line.id]
                else:
                    move_lines_ids_d[line.partner_id.id] = [line.id]

            print 'move_ids', move_ids
            print 'move_line_ids', move_line_ids
            print 'move_lines_ids_d', move_lines_ids_d

            account_id = self.get_payable_account_id(cr, uid, context=context)
            # TODO: account_id need to be particular value?.
            journal_id = self.get_purchase_journal_id(cr, uid, context=context)
            #~ TODO: Ask. need to be a particular value? need to be selecte
            #~ the allow reconcillaton option?
            period_id = per_obj.find(cr, uid, context=context)[0]

            for partner_id in move_lines_ids_d:
                aml_obj.reconcile(cr, uid, move_lines_ids_d[partner_id],
                                  'manual', account_id, period_id, journal_id,
                                  context=context)

            # reconcile manual for employee, like supplier payment... simulate

        return True

    def validate_expense_invoices(self, cr, uid, ids, context=None):
        """ Validate Invoices asociated to the Expense. Put the invoices in
        Open State. """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wf_service = netsvc.LocalService("workflow")
        for exp_brw in self.browse(cr, uid, ids, context=context):
            validate_inv_ids = \
                [inv_brw.id
                 for inv_brw in exp_brw.invoice_ids
                 if inv_brw.state == 'draft']
            for inv_id in validate_inv_ids:
                wf_service.trg_validate(uid, 'account.invoice', inv_id,
                                        'invoice_open', cr)
        return True

    def generate_accounting_entries(self, cr, uid, ids, context=None):
        """ Active the workflow signals to change the expense to Done state
        and generate accounting entries for the expense by clicking the
        'Generate Accounting Entries' button. """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wf_service = netsvc.LocalService("workflow")
        for exp_brw in self.browse(cr, uid, ids, context=context):
            if exp_brw.state not in ['done']:
                wf_service.trg_validate(uid, 'hr.expense.expense', exp_brw.id,
                                        'confirm', cr)
                wf_service.trg_validate(uid, 'hr.expense.expense', exp_brw.id,
                                        'validate', cr)
                wf_service.trg_validate(uid, 'hr.expense.expense', exp_brw.id,
                                        'done', cr)
        return True

    def create_match_move(self, cr, uid, ids, context=None):
        """ Create new account move that containg the data of the expsense
        account move created and expense invoices moves. Receives only one
        id """
        context = context or {}
        am_obj = self.pool.get('account.move')
        exp_brw = self.browse(cr, uid, ids, context=context)
        vals = dict()
        vals['ref'] = 'Pago de Viaticos'
        vals['journal_id'] = self.get_purchase_journal_id(
            cr, uid, context=context)
        debit_lines = self.create_debit_lines_dict(
            cr, uid, exp_brw.id, context=context)

        print '\n'*5
        print 'exp_brw', exp_brw
        print 'exp_brw.account_move_id', exp_brw.account_move_id
        print 'exp.move.partner_id', exp_brw.account_move_id.partner_id
        credit_line = [
            (0, 0, {
             'name': 'Pago de Viaticos',
             'account_id': self.get_payable_account_id(
                 cr, uid, context=context),
             'partner_id': exp_brw.account_move_id.partner_id.id,
             'debit': 0.0,
             'credit': self.get_lines_credit_amount(
                 cr, uid, exp_brw.account_move_id.id, context=context)
             })
            #~ TODO: I think may to change this acocunt_id
        ]
        vals['line_id'] = debit_lines + credit_line
        return am_obj.create(cr, uid, vals, context=context)

    def create_debit_lines_dict(self, cr, uid, ids, context=None):
        """ Returns a list of dictionarys for create account move
        lines objects. Only recive one exp id """
        context = context or {}
        debit_lines = []
        am_obj = self.pool.get('account.move')
        exp_brw = self.browse(cr, uid, ids, context=context)
        move_ids = [inv_brw.move_id.id
                    for inv_brw in exp_brw.invoice_ids
                    if inv_brw.move_id]
        for inv_move_brw in am_obj.browse(cr, uid, move_ids, context=context):
            debit_lines.append(
                (0, 0, {
                 'name': 'Pago de Viaticos',
                 'account_id': self.get_payable_account_id(
                     cr, uid, context=context),
                 'partner_id': inv_move_brw.partner_id.id,
                 'invoice': inv_move_brw.line_id[0].invoice.id,
                 'debit':  self.get_lines_credit_amount(
                     cr, uid, inv_move_brw.id, context=context),
                 'credit': 0.0})
            )
            #~ TODO: invoice field is have not been set, check why
        return debit_lines

    def get_lines_credit_amount(self, cr, uid, move_id, context=None):
        """ Return the credit amount (float value) of the account move given.
        @param move_id: list of move id where the credit will be extract """
        context = context or {}
        am_obj = self.pool.get('account.move')
        move_brw = am_obj.browse(cr, uid, move_id, context=context)
        amount = [move_line.credit
                  for move_line in move_brw.line_id
                  if move_line.credit != 0.0]
        if not amount:
            raise osv.except_osv(
                'Invalid Procedure!',
                "There is a problem in your move definition " +
                move_brw.ref + ' ' + move_brw.name)
        return amount[0]

    def get_payable_account_id(self, cr, uid, context=None):
        """ Return the id of a payable account. """
        aa_obj = self.pool.get('account.account')
        return aa_obj.search(cr, uid, [('type', '=', 'payable')], limit=1,
                             context=context)[0]

    def get_purchase_journal_id(self, cr, uid, context=None):
        """ Return an journal id of type purchase. """
        context = context or {}
        aj_obj = self.pool.get('account.journal')
        return aj_obj.search(cr, uid, [('type', '=', 'purchase')], limit=1,
                             context=context)[0]
