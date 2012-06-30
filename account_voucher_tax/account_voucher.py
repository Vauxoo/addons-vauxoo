# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Rodo (rodo@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields

class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    
    def voucher_move_line_create(self, cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None):
        print company_currency,"moneda base"
        print current_currency,"moneda base"
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        invoice_obj = self.pool.get('account.invoice')
        currency_obj = self.pool.get('res.currency')
        res=super(account_voucher, self).voucher_move_line_create(cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None)
        for voucher in self.browse(cr,uid,[voucher_id],context=context):
            lines=[]
            for line in voucher.line_ids:
                if line.amount>0:
                    invoice_ids=invoice_obj.search(cr,uid,[('move_id','=',line.move_line_id.move_id.id)],context=context)
                    for invoice in invoice_obj.browse(cr,uid,invoice_ids,context=context):
                        for tax in invoice.tax_line:
                            if tax.tax_id.tax_voucher_ok:
                                move_ids=[]
                                account=tax.tax_id.account_collected_voucher_id.id
                                credit_amount=((tax.tax_id.amount*tax.base)*(line.amount/line.amount_original))/invoice.currency_id.rate
                                debit_amount=0.0
                                if tax.tax_id.amount<0:
                                    credit_amount=0.0
                                    debit_amount=(-1.0*(tax.tax_id.amount*tax.base)*(line.amount/line.amount_original))/invoice.currency_id.rate
                                if invoice.type=='out_invoice':## considerar que hacer con refund
                                    account=tax.tax_id.account_paid_voucher_id.id
                                    credit_amount, debit_amount=debit_amount, credit_amount
                                amount2 = self._convert_amount(cr, uid, credit_amount, voucher.id, context=context)
                                print amount2,"parece que asi se hace,,,,"
                                move_line={
                                    'journal_id': voucher.journal_id.id,
                                    'period_id': voucher.period_id.id,
                                    'name': tax.name or '/',
                                    'account_id': tax.account_id.id,
                                    'move_id': int(move_id),
                                    'partner_id': voucher.partner_id.id,
                                    'company_id':company_currency,
                                    'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                                    'quantity': 1,
                                    'credit': credit_amount,
                                    'debit': debit_amount,
                                    'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                                    'date': voucher.date,
                                    }
                                if company_currency!=current_currency:
                                    amount_currency = currency_obj.compute(cr, uid, company_currency, line.move_line_id.currency_id.id, credit_amount, context=context)
                                    print amount_currency,"monto"
                                    move_line['amount_currency'] = credit_amount/voucher.payment_rate
                                move_ids.append(move_line_obj.create(cr,uid,move_line,context=context))
                                move_line={
                                    'journal_id': voucher.journal_id.id,
                                    'period_id': voucher.period_id.id,
                                    'name': tax.name or '/',
                                    'account_id': account,
                                    'move_id': int(move_id),
                                    'partner_id': voucher.partner_id.id,
                                    'company_id':company_currency,
                                    #'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                                    'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                                    'quantity': 1,
                                    'credit': debit_amount,
                                    'debit': credit_amount,
                                    'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                                    'date': voucher.date,

                                    }
                                move_line_obj.create(cr,uid,move_line,context=context)
                                for mov_line in invoice.move_id.line_id:
                                    print mov_line.account_id.id,"cuentaa"
                                    if mov_line.account_id.id==tax.account_id.id:
                                        move_ids.append(mov_line.id)
                                        print mov_line.id,"esta si"
                                if line.amount==line.amount_original:
                                    self.pool.get('account.move.line').reconcile(cr, uid, move_ids, 'manual', writeoff_acc_id=tax.account_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
                                else:
                                    self.pool.get('account.move.line').reconcile_partial(cr, uid, move_ids, 'manual', context)
        return res
account_voucher()

class account_move_line(osv.osv):
    _inherit = 'account.move.line'
    
    def reconcile_partial(self, cr, uid, ids, type='auto', context=None, writeoff_acc_id=False, writeoff_period_id=False, writeoff_journal_id=False):
        res=super(account_move_line, self).reconcile_partial(cr, uid, ids, type='auto', context=None, writeoff_acc_id=False, writeoff_period_id=False, writeoff_journal_id=False)
        print res,"resssspuesta"
        return res
account_move_line()


class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def pay_and_reconcile(self, cr, uid, ids, pay_amount, pay_account_id, period_id, pay_journal_id, writeoff_acc_id, writeoff_period_id, writeoff_journal_id, context=None, name=''):
        res=super(account_invoice, self).pay_and_reconcile(self, cr, uid, ids, pay_amount, pay_account_id, period_id, pay_journal_id, writeoff_acc_id, writeoff_period_id, writeoff_journal_id, context=None, name='')
        print res,"resssspuestaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        return res
account_invoice()
