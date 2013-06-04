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
from tools.translate import _
import release
import decimal_precision as dp
import time

class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    
    #~ _columns={
        #~ 'move_id2':fields.many2one('account.move', 'Account Entry Tax'),
        #~ 'move_ids2': fields.related('move_id2','line_id', type='one2many', relation='account.move.line', string='Journal Items Tax', readonly=True),
#~ 
        #~ }
    
    def get_rate(self, cr, uid, move_id, context=None):
        move_obj = self.pool.get('account.move')
        if not context:
            context = {}
        for move in move_obj.browse(cr, uid, [move_id], context):
            for line in move.line_id:
                amount_base = line.debit or line.credit or 0
                rate = 1
                if amount_base and line.amount_currency:
                    rate=amount_base/line.amount_currency
                    return rate
        return rate
    
    def get_percent_pay_vs_invoice(self, cr, uid, amount_original,amount, context=None):
        return amount_original and amount/amount_original or 1.0
    
    def get_partial_amount_tax_pay(self, cr, uid, tax_amount,tax_base, context=None):
        return tax_amount*tax_base
    
    def voucher_move_line_tax_create(self, cr, uid, voucher_id, move_id, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        invoice_obj = self.pool.get('account.invoice')
        currency_obj = self.pool.get('res.currency')
        company_currency = self._get_company_currency(cr, uid, voucher_id, context)
        current_currency = self._get_current_currency(cr, uid, voucher_id, context)
        move_ids=[]
        for voucher in self.browse(cr, uid, [voucher_id], context=context):
            for line in voucher.line_ids:
                for line_tax in line.tax_line_ids:
                    move_ids=[]
                    credit=line_tax.amount_tax
                    amount_tax_unround=line_tax.amount_tax_unround
                    debit=0.0
                    if company_currency!=current_currency:
                        credit=currency_obj.compute(cr, uid, current_currency,company_currency, float('%.*f' % (2,credit)), round=True, context=context)
                    account_tax_voucher=line_tax.tax_id.account_collected_voucher_id.id
                    account_tax_collected=line_tax.tax_id.account_collected_id.id
                    if credit < 0:
                        credit, debit=debit, credit
                    if voucher.type=='payment':
                        credit, debit=debit, credit
                    move_line={
                    'journal_id': voucher.journal_id.id,
                    'period_id': voucher.period_id.id,
                    'name': line_tax.tax_id.account_collected_voucher_id.name or '/',
                    'account_id': account_tax_voucher,
                    'move_id': int(move_id),
                    'partner_id': voucher.partner_id.id,
                    'company_id':company_currency,
                    'currency_id': line.move_line_id and (company_currency <> current_currency and current_currency) or False,
                    #~ 'currency_id': voucher.journal_id.currency.id,
                    'quantity': 1,
                    'credit': float('%.*f' % (2,abs(credit))),
                    'debit': float('%.*f' % (2,abs(debit))),
                    'amount_tax_unround':amount_tax_unround,
#                    'analytic_account_id': line_tax.analytic_account_id and line_tax.analytic_account_id.id or False,
                    'date': voucher.date,
                    'tax_id': line_tax.id
                    }
                    if company_currency!=current_currency:
                        move_line['amount_currency']=line_tax.amount_tax
                    move_ids.append(move_line_obj.create(cr ,uid, move_line, context=context))
                    #~ if line_tax.diff_amount_tax:
                    context['date']=line.move_line_id.date
                    #~ amount=currency_obj.compute(cr, uid, current_currency,company_currency, float('%.*f' % (2,line_tax.original_tax)), round=False, context=context)
                    #~ if credit and voucher.payment_option=='with_writeoff'and line_tax.diff_amount_tax:
                        #~ credit=amount
                    #~ if debit and voucher.payment_option=='with_writeoff' and line_tax.diff_amount_tax:
                        #~ debit=amount
                    credit, debit=debit, credit
                    entrie_name = line_tax.tax_id.name
                    #########borrado mientras se hizo en una funcion del writeoff
                #    if voucher.payment_option=='with_writeoff':
                 #       if debit:
                  #          debit=line_tax.balance_tax
                   #     else:
                    #        credit=line_tax.balance_tax
                     #   print debit,credit,'imprimo debit,credit'
                      #  entrie_name = 'poliza de writeof'
                    #############################################################
                    move_line={
                    'journal_id': voucher.journal_id.id,
                    'period_id': voucher.period_id.id,
                    'name': entrie_name or '/',
                    'account_id':account_tax_collected, 
                    'move_id': int(move_id),
                    'partner_id': voucher.partner_id.id,
                    'company_id':company_currency,
                    #~ 'currency_id': voucher.journal_id.currency.id,
                    'currency_id': line.move_line_id and (company_currency <> current_currency and current_currency) or False,
                    'quantity': 1,
                    'credit': float('%.*f' % (2,abs(credit))),
                    'debit': float('%.*f' % (2,abs(debit))),
 #                   'amount_tax_unround':amount_tax_unround,
                    'analytic_account_id': line_tax.analytic_account_id and line_tax.analytic_account_id.id or False,
                    'date': voucher.date,
                    'tax_id': line_tax.id
                    }
                    if company_currency!=current_currency:
                        move_line['amount_currency']=line_tax.amount_tax
                    move_ids.append(move_line_obj.create(cr ,uid, move_line, context=context))
                    
                    if line_tax.balance_tax + line_tax.amount_tax < line_tax.original_tax and voucher.payment_option=='with_writeoff':
                        context['date']=line.move_line_id.date
                        credit_orig=currency_obj.compute(cr, uid, current_currency,company_currency, float('%.*f' % (2,line_tax.balance_tax)), round=True, context=context)
                        context['date']=voucher.date
                        credit_now=currency_obj.compute(cr, uid, current_currency,company_currency, float('%.*f' % (2,line_tax.amount_tax)), round=False, context=context)
                        amount_diff=abs(credit_orig-credit_now)
                        debit_diff=0.0
                        if voucher.type=='payment':
                            if not credit_orig-credit_now < 0: 
                                amount_diff, debit_diff= debit_diff, amount_diff
                            move_line={
                                'journal_id': voucher.journal_id.id,
                                'period_id': voucher.period_id.id,
                                'name': 'change_tax: ' + str(line.name),
                                'account_id':line_tax.diff_account_id and line_tax.diff_account_id.id or voucher.writeoff_acc_id.id, 
                                'move_id': int(move_id),
                                'partner_id': voucher.partner_id.id,
                                'company_id':company_currency,
                                #~ 'currency_id': voucher.journal_id.currency.id,
                                'currency_id': line.move_line_id and (company_currency <> current_currency and current_currency) or False,
                                'quantity': 1,
                                'credit': float('%.*f' % (2,amount_diff)),
                                'debit': float('%.*f' % (2,debit_diff)),
                                #~ 'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                                'date': voucher.date,
                                'tax_id': line_tax.id,
                                'amount_tax_unround':amount_tax_unround,
                                }
                            move_line_obj.create(cr ,uid, move_line, context=context)
                        else:
                            if credit_orig-credit_now < 0:
                                amount_diff, debit_diff= debit_diff, amount_diff
                            move_line={
                                'journal_id': voucher.journal_id.id,
                                'period_id': voucher.period_id.id,
                                'name': 'change_tax: ' +  str(line.name),
                                'account_id':line_tax.diff_account_id and line_tax.diff_account_id.id or voucher.writeoff_acc_id.id, 
                                'move_id': int(move_id),
                                'partner_id': voucher.partner_id.id,
                                'company_id':company_currency,
                                #~ 'currency_id': voucher.journal_id.currency.id,
                                'currency_id': line.move_line_id and (company_currency <> current_currency and current_currency) or False,
                                'quantity': 1,
                                'credit': float('%.*f' % (2,amount_diff)),
                                'debit': float('%.*f' % (2,debit_diff)),
                                #~ 'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                                'date': voucher.date,
                                'tax_id': line_tax.id
                                }
                            #move_line_obj.create(cr ,uid, move_line, context=context)
                    if voucher.writeoff_amount > 0:
                        reference_amount = self.get_partial_amount_tax_pay(cr, uid, voucher.writeoff_amount, line_tax.original_tax, context=context)
                        move_lines = self._get_move_writeoff(cr, uid, move_id, voucher, line, line_tax, company_currency, reference_amount, context=context)
                        for move_line_w in move_lines:
                            move_line_obj.create(cr ,uid, move_line_w, context=context)
        return move_ids
    
    def _get_move_writeoff(self, cr, uid, move_id, voucher, line, line_tax, company_currency, reference_amount, context=None):
        print reference_amount,'imprimo reference_amount'
        debit_line_vals = {
                    'name': line_tax.tax_id.name,
                    'quantity': 1,
                    'date': time.strftime('%Y-%m-%d'),
                    'partner_id': voucher.partner_id.id,
                    'debit': abs(reference_amount),
                    'credit': 0.0,
                    'account_id': voucher.writeoff_acc_id.id,
                    'journal_id': voucher.journal_id.id,
                    'period_id': voucher.period_id.id,
                    'company_id':company_currency,
                    'move_id': int(move_id),
        }
        credit_line_vals = {
                    'name': line_tax.tax_id.name,
                    'quantity': 1,
                    'date': time.strftime('%Y-%m-%d'),
                    'partner_id': voucher.partner_id.id,
                    'credit': abs(reference_amount),
                    'debit': 0.0,
                    'account_id': line_tax.tax_id.account_collected_voucher_id.id,
                    'journal_id': voucher.journal_id.id,
                    'period_id': voucher.period_id.id,
                    'company_id':company_currency,
                    'move_id': int(move_id),
        }
        return [debit_line_vals, credit_line_vals]
    
    def voucher_move_line_create(self, cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        invoice_obj = self.pool.get('account.invoice')
        currency_obj = self.pool.get('res.currency')
        res=super(account_voucher, self).voucher_move_line_create(cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None)
        new=self.voucher_move_line_tax_create(cr,uid, voucher_id, move_id, context=context)
        print new,'new'
        #~ res[1][0]=res[1][0]+new
        return res
        
    def compute_tax(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        invoice_obj = self.pool.get('account.invoice')
        currency_obj = self.pool.get('res.currency')
        tax_line_obj = self.pool.get('account.voucher.line.tax')
        for voucher in self.browse(cr, uid, ids, context=context):
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
            lines=[]
            for line in voucher.line_ids:
                delete_ids=tax_line_obj.search(cr , uid, [('voucher_line_id', '=' , line.id)], context=context)
                tax_line_obj.unlink(cr, uid, delete_ids, context=context)
                factor=self.get_percent_pay_vs_invoice(cr,uid,line.amount_original, line.amount,context=context)
                if line.amount>0:
                    invoice_ids=invoice_obj.search(cr,uid,[('move_id','=',line.move_line_id.move_id.id)],context=context)
                    for invoice in invoice_obj.browse(cr,uid,invoice_ids,context=context):
                        for tax in invoice.tax_line:
                            if tax.tax_id.tax_voucher_ok:
                                base_amount=self.get_partial_amount_tax_pay(cr, uid, tax.tax_id.amount, tax.base, context=context)
                                move_ids=[]
                                account=tax.tax_id.account_collected_voucher_id.id
                                credit_amount= float('%.*f' % (2,(base_amount*factor)))
                                credit_amount_original = (base_amount*factor)
                                amount_unround= float(base_amount*factor)
                            ########## la comento para hacer pruebas sin el redondeo propuesto aqui
                            #    if credit_amount:
                             #       if abs(float('%.*f' % (2,credit_amount))-base_amount)<=.02:
                              #          credit_amount=credit_amount-abs(float('%.*f' % (2,credit_amount))-base_amount)
                               #         amount_unround=amount_unround-abs(float(amount_unround)-base_amount)
                                #    if abs(float('%.*f' % (2,credit_amount))+ (base_amount*(1-factor))-base_amount)<.02:
                                 #       credit_amount=credit_amount-abs(float('%.*f' % (2,credit_amount))+ (base_amount*(1-factor))-base_amount)
                                  #      amount_unround=amount_unround-abs(float(amount_unround)+ (base_amount*(1-factor))-base_amount)
                            #######################################################################
                                #context['date']=invoice.date_invoice
                                diff_amount_tax=0.0
                                diff_account_id=False
                                base_amount_curr=base_amount
                                if company_currency==current_currency:
                                    rate_move=self.get_rate(cr,uid,line.move_line_id.move_id.id,context=context)
                                    credit_amount=credit_amount*rate_move
                                    amount_unround=amount_unround*rate_move
                                else:
                                    credit_amount=currency_obj.compute(cr, uid, invoice.currency_id.id,current_currency, float('%.*f' % (2,credit_amount)), round=False, context=context)
                                    amount_unround=currency_obj.compute(cr, uid, invoice.currency_id.id,current_currency, float(amount_unround), round=False, context=context)
                                    base_amount_curr=currency_obj.compute(cr, uid, invoice.currency_id.id,current_currency, float('%.*f' % (2,base_amount)), round=False, context=context)
                                    context['date']=invoice.date_invoice
                                    credit_orig=currency_obj.compute(cr, uid, current_currency,company_currency, float('%.*f' % (2,credit_amount)), round=False, context=context)
                                    context['date']=voucher.date
                                    credit_diff=currency_obj.compute(cr, uid, current_currency,company_currency, float('%.*f' % (2,credit_amount)), round=False, context=context)

                                    diff_amount_tax=currency_obj.compute(cr, uid, company_currency,current_currency, float('%.*f' % (2,(credit_orig-credit_diff))), round=False, context=context)
                                    if credit_orig>credit_diff:
                                        if voucher.type=='receipt':
                                            diff_account_id=tax.tax_id.account_expense_voucher_id.id
                                        else:
                                            diff_account_id=tax.tax_id.account_income_voucher_id.id
                                    if credit_orig<credit_diff:
                                        if voucher.type=='receipt':
                                            diff_account_id=tax.tax_id.account_income_voucher_id.id
                                        else:
                                            diff_account_id=tax.tax_id.account_expense_voucher_id.id
                                        
                                debit_amount=0.0
                                move_line_id= False
                                for move_lines in line.move_line_id.move_id.line_id:
                                    if move_lines.account_id.id== account:
                                        move_line_id=move_lines.id
                                        break
                                tax_line={
                                    'tax_id':tax.tax_id.id,
                                    'account_id':account,
                                    'amount_tax':credit_amount_original,
                                    'amount_tax_unround':amount_unround,
                                    'tax':credit_amount,
                                    'voucher_line_id':line.id,
                                    'original_tax':base_amount_curr,
                                    'diff_account_id':diff_account_id,
                                    'diff_amount_tax':abs(diff_amount_tax),
                                    'move_line_id': move_line_id,
                                    'analytic_account_id': tax.account_analytic_id and tax.account_analytic_id.id or False
                                    
                                }
                                tax_line_compute = tax_line_obj.create(cr, uid, tax_line, context=context)
        return True
        
account_voucher()

class account_voucher_line(osv.osv):
    _inherit = 'account.voucher.line'
    
    _columns={
        'tax_line_ids':fields.one2many('account.voucher.line.tax', 'voucher_line_id', 'Tax Lines'),
        }
account_voucher_line()

class account_move_line(osv.osv):
    _inherit = 'account.move.line'
    
    def _get_query_round(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        cr.execute("""
                select account_id, sum(amount_tax_unround) as without,
                    case  when sum(credit) > 0.0
                        then sum(credit)
                    when sum(debit) > 0.0
                        then sum(debit)
                    end as round, id
                from account_move_line
                where move_id in (
                select move_id from account_move_line aml
                where id in %s)
                and amount_tax_unround is not null
                group by account_id, id
                order by id asc """,(tuple(ids),))
        dat = cr.dictfetchall()
        return dat
    
    def reconcile(self, cr, uid, ids, type='auto', writeoff_acc_id=False, writeoff_period_id=False, writeoff_journal_id=False, context=None):
        res=super(account_move_line, self).reconcile(cr, uid, ids=ids, 
        type='auto', writeoff_acc_id=writeoff_acc_id, writeoff_period_id=writeoff_period_id, 
        writeoff_journal_id=writeoff_journal_id, context=context)
#        if not writeoff_acc_id:
        dat = self._get_query_round(cr, uid, ids, context=context)
        res_round = {}
        res_without_round = {}
        res_ids = {}
        print res,'imprimo res'
        for val_round in dat:
            print val_round,'imprimo val_round'
            res_round.setdefault(val_round['account_id'], 0)
            res_without_round.setdefault(val_round['account_id'], 0)
            res_ids.setdefault(val_round['account_id'], 0)
            res_round[val_round['account_id']] += val_round['round']
            res_without_round[val_round['account_id']] += val_round['without']
            res_ids[val_round['account_id']] = val_round['id']
        for res_diff_id in res_round.items():
            diff_val = abs(res_without_round[res_diff_id[0]]) - abs(res_round[res_diff_id[0]])
            diff_val = round(diff_val, 2)
            print diff_val,'imprimo diff_val'
            if diff_val <> 0.00:
                print diff_val,'imprimo diff_val'
                move_diff_id = [res_ids[res_diff_id[0]]]
                for move in self.browse(cr, uid, move_diff_id, context=context):
                    move_line_ids = self.search(cr, uid, [('move_id', '=', move.move_id.id),('tax_id', '=', move.tax_id.id)])
                    for diff_move in self.browse(cr, uid, move_line_ids, context=context):
                        print diff_move.debit, diff_move.credit,'imprimo diff_move2222222222222222'
                        if diff_move.debit == 0.0 and diff_move.credit :
                            self.write(cr, uid, [diff_move.id], {'credit': diff_move.credit+diff_val})
                        if diff_move.credit == 0.0 and diff_move.debit:
                            self.write(cr, uid, [diff_move.id], {'debit': diff_move.debit+diff_val})
        return res
    
    _columns={
        'amount_tax_unround':fields.float('Amount tax undound', digits=(12, 16)),
        'tax_id': fields.many2one('account.voucher.line.tax', 'Tax')
        }
account_move_line()


class account_voucher_line_tax(osv.osv):
    _name= 'account.voucher.line.tax'
    
    def _compute_balance(self, cr, uid, ids, name, args, context=None):
        res={}

        for line_tax in self.browse(cr, uid, ids, context=context):
            sum=0.0
            old_ids=self.search(cr, uid, [('move_line_id', '=', line_tax.move_line_id.id),('id', '!=', line_tax.id)])
            for lin_sum in self.browse(cr, uid, old_ids, context=context):
                sum+=lin_sum.amount_tax
            res[line_tax.id]=line_tax.original_tax-sum
        return res
    
    
    def onchange_amount_tax(self, cr, uid, ids, amount, tax):
        res={}
        res['value']={'amount_tax':amount, 'amount_tax_unround':amount, 'diff_amount_tax':abs(tax-amount)}
        return res
    
    _columns={
        'tax_id':fields.many2one('account.tax','Tax'),
        'account_id':fields.many2one('account.account','Account'),
        'amount_tax':fields.float('Amount Tax', digits=(12, 16)),
        'amount_tax_unround':fields.float('Amount tax undound'),
        'original_tax':fields.float('Original Import Tax'),
        'tax': fields.float('Tax'),
        'balance_tax':fields.function(_compute_balance, type='float', string='Balance Import Tax', store=True, digits=(12, 6)),
        #~ 'balance_tax':fields.float('Balance Import Tax'),
        'diff_amount_tax':fields.float('Difference',digits_compute= dp.get_precision('Account')),
        'diff_account_id':fields.many2one('account.account','Account Diff'),
        'voucher_line_id':fields.many2one('account.voucher.line', 'Voucher Line'),
        'move_line_id':fields.many2one('account.move.line','Move'),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Account Analytic')
        
    }
account_voucher_line_tax()
