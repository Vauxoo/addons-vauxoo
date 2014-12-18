# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
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

from openerp.osv import osv
import time


class account_bank_statement_line(osv.osv):

    _inherit = 'account.bank.statement.line'

    # pylint: disable=W0622
    def process_reconciliation(self, cr, uid, id, mv_line_dicts, context=None):

        if context is None:
            context = {}

        move_line_obj = self.pool.get('account.move.line')
        move_obj = self.pool.get('account.move')
        voucher_obj = self.pool.get('account.voucher')
        move_line_ids = []

        st_line = self.browse(cr, uid, id, context=context)
        company_currency = st_line.journal_id.company_id.currency_id.id
        statement_currency = st_line.journal_id.currency.id or company_currency

        vals_move = {
            'date': time.strftime('%Y-%m-%d'),
            'period_id': st_line.statement_id.period_id.id,
            'journal_id': st_line.statement_id.journal_id.id,
            }
        move_id_old = move_obj.create(cr, uid, vals_move, context)
        
        move_amount_counterpart = self._get_move_line_counterpart(
            cr, uid, mv_line_dicts, context=context)
        move_line_tax_dict = self._get_move_line_tax(
            cr, uid, mv_line_dicts, context=context)

        factor = voucher_obj.get_percent_pay_vs_invoice(
            cr, uid, move_amount_counterpart[1],
            move_amount_counterpart[0], context=context)

        for move_line_tax in move_line_tax_dict:
            account_tax_voucher =\
                move_line_tax.get('account_tax_voucher')
            account_tax_collected =\
                move_line_tax.get('account_tax_collected')

            type = 'sale'
            if st_line.amount < 0:
                type = 'payment'
            
            lines_tax = voucher_obj._preparate_move_line_tax(
                cr, uid,
                account_tax_voucher, # cuenta del impuesto(account.tax)
                account_tax_collected, # cuenta del impuesto para notas de credito/debito(account.tax)
                move_id_old, type,
                st_line.partner_id.id,
                st_line.statement_id.period_id.id,
                st_line.statement_id.journal_id.id,
                st_line.date, company_currency,
                move_line_tax.get('amount') * factor, # Monto del impuesto por el factor(cuanto le corresponde)(aml)
                move_line_tax.get('amount') * factor, # Monto del impuesto por el factor(cuanto le corresponde)(aml)
                statement_currency, False,
                move_line_tax.get('tax_id'), # Impuesto
                move_line_tax.get('tax_analytic_id'), # Cuenta analitica del impuesto(aml)
                move_line_tax.get('amount_base'), # Monto base(aml)
                factor, context=context)
            for move_line_tax in lines_tax:
                move_line_ids.append(
                    move_line_obj.create(
                        cr, uid, move_line_tax, context=context
                        ))

        context['apply_round'] = True
        res = super(account_bank_statement_line, self).process_reconciliation(
            cr, uid, id, mv_line_dicts, context=context)
        move_line_obj.write(cr, uid, move_line_ids,
                            {'move_id': st_line.journal_entry_id.id})
        update_ok = st_line.journal_id.update_posted
        if not update_ok:
            st_line.journal_id.write({'update_posted': True})
        move_obj.button_cancel(cr, uid, [move_id_old])
        st_line.journal_id.write({'update_posted': update_ok})
        move_obj.unlink(cr, uid, move_id_old)
        move_line_reconcile_id = [dat.reconcile_id.id
                                  for dat in st_line.journal_entry_id.line_id
                                  if dat.reconcile_id]
        if move_line_reconcile_id:
            move_line_statement_bank = move_line_obj.search(
                cr, uid, [('reconcile_id', 'in', move_line_reconcile_id)])

            context['apply_round'] = False
            move_line_obj._get_round(cr, uid,
                                     move_line_statement_bank, context=context)
        return res

    def _get_move_line_counterpart(self, cr, uid, mv_line_dicts, context=None):

        move_line_obj = self.pool.get('account.move.line')
        
        counterpart_amount = 0
        statement_amount = 0
        for move_line_dict in mv_line_dicts:

            if move_line_dict.get('counterpart_move_line_id'):
                move_counterpart_id = move_line_dict.get('counterpart_move_line_id')
                move_line_id = move_line_obj.browse(
                    cr, uid, move_counterpart_id, context=context)
                
                if move_line_id.journal_id.type not in ('sale_refund', 'purchase_refund'):
                    statement_amount += move_line_dict.get('credit') > 0 and move_line_dict.get('credit') or move_line_dict.get('debit')
                    counterpart_amount += move_line_id.credit > 0 and\
                        move_line_id.credit or move_line_id.debit

        return [statement_amount, counterpart_amount]

    def _get_move_line_tax(self, cr, uid, mv_line_dicts, context=None):
        move_obj = self.pool.get('account.move')
        tax_obj = self.pool.get('account.tax')
        move_line_obj = self.pool.get('account.move.line')

        dat = []
        move_tax_amount = []
        account_group = {}
        move_line_ids = []

        counterpart_move_line_ids = [
            mv_line_dict.get('counterpart_move_line_id')
            for mv_line_dict in mv_line_dicts
            if mv_line_dict.get('counterpart_move_line_id')]

        for move_line in move_line_obj.browse(
            cr, uid, counterpart_move_line_ids, context=context):
    
            move_line_ids.extend(move_line_obj.search(
                cr, uid, [('move_id', '=', move_line.move_id.id)]))

        for move_line_id in move_line_obj.browse(cr, uid, move_line_ids):
            if move_line_id.account_id.type not in ('receivable', 'payable'):
                account_group.setdefault(move_line_id.account_id.id, 0)
                account_group[move_line_id.account_id.id] += move_line_id.debit > 0 and move_line_id.debit or move_line_id.credit*-1
                
        for move_account_tax in account_group:
            tax_ids = tax_obj.search(
                cr, uid,
                [('account_collected_id', '=', move_account_tax),
                 ('tax_voucher_ok', '=', True)], limit=1)
            
            if tax_ids:
                tax_id = tax_obj.browse(cr, uid, tax_ids[0])
                dat.append({
                    'account_tax_voucher':
                        tax_id.account_paid_voucher_id.id,
                    'account_tax_collected':
                        tax_id.account_collected_id.id,
                    'amount': abs(account_group.get(move_account_tax)),
                    'tax_id': tax_id,
                    'tax_analytic_id':
                        tax_id.account_analytic_collected_id and
                        tax_id.account_analytic_collected_id.id or False,
                    'amount_base': 300
                    })
        return dat
