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

        for mv_line_dict in mv_line_dicts:
            if mv_line_dict.get('counterpart_move_line_id'):
                move_line_id = mv_line_dict.get('counterpart_move_line_id', [])
                move_id_reconcile = move_line_obj.browse(
                    cr, uid, move_line_id, context=context)
                print move_id_reconcile.debit, move_id_reconcile.credit,"qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq"
                move_id = move_line_obj.browse(
                    cr, uid, move_line_id, context=context).move_id.id
                for move_line_tax in self._get_move_line_tax(
                        cr, uid, move_id, context=context):
                    account_tax_voucher =\
                        move_line_tax.get('account_tax_voucher')
                    account_tax_collected =\
                        move_line_tax.get('account_tax_collected')
                    amount_original_inv = move_id_reconcile.credit > 0 and\
                        move_id_reconcile.credit or\
                        move_id_reconcile.debit
                    amount_statement_bank = st_line.amount
                    type = 'sale'
                    if st_line.amount > amount_original_inv:
                        amount_statement_bank = amount_original_inv
                    if st_line.amount < 0:
                        type = 'payment'
                        amount_statement_bank =\
                            amount_statement_bank * -1

                    factor = voucher_obj.get_percent_pay_vs_invoice(
                        cr, uid, amount_original_inv,
                        amount_statement_bank, context=context)
                    lines_tax = voucher_obj._preparate_move_line_tax(
                        cr, uid,
                        account_tax_voucher, # cuenta del impuesto(account.tax)
                        account_tax_collected, # cuenta del impuesto para notas de credito/debito(account.tax)
                        move_id_old, type,
                        move_id_reconcile.partner_id.id,
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

    def _get_move_line_tax(self, cr, uid, move, context=None):
        move_obj = self.pool.get('account.move')
        tax_obj = self.pool.get('account.tax')

        dat = []
        move_line = move_obj.browse(cr, uid, move, context=context)
        for move_line_id in move_line.line_id:
            if move_line_id.account_id.type not in ('receivable', 'payable'):
                tax_ids = tax_obj.search(
                    cr, uid,
                    [('account_collected_id', '=', move_line_id.account_id.id),
                     ('tax_voucher_ok', '=', True)], limit=1)
                if tax_ids:
                    tax_id = tax_obj.browse(cr, uid, tax_ids[0])
                    dat.append({
                        'account_tax_voucher':
                            tax_id.account_paid_voucher_id.id,
                        'account_tax_collected':
                            tax_id.account_collected_id.id,
                        'amount': move_line_id.debit > 0 and
                            move_line_id.debit or move_line_id.credit,
                        'tax_id': tax_id,
                        'tax_analytic_id':
                            tax_id.account_analytic_collected_id and
                            tax_id.account_analytic_collected_id.id or False,
                        'amount_base': move_line_id.amount_base
                        })
                    print dat,"wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww"
        return dat

