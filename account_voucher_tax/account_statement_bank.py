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

        self._get_factor_type(cr, uid, st_line.amount, False, context=context)
        type = 'sale'
        if st_line.amount < 0:
            type = 'payment'

        move_amount_counterpart = self._get_move_line_counterpart(
            cr, uid, mv_line_dicts, context=context)
        move_line_tax_dict = self._get_move_line_tax(
            cr, uid, mv_line_dicts, context=context)

        factor = voucher_obj.get_percent_pay_vs_invoice(
            cr, uid, move_amount_counterpart[1],
            move_amount_counterpart[0], context=context)

        for move_line_tax in move_line_tax_dict:
            line_tax_id = move_line_tax.get('tax_id')
            # Cuando el impuesto (@tax_id) tiene @amount = 0 es un impuesto
            # de compra 0% o EXENTO y necesitamos enviar el monto base
            amount_base_secondary =\
                line_tax_id.amount and\
                move_amount_counterpart[1] / (1+line_tax_id.amount) or\
                move_line_tax.get('amount_base_secondary')
            account_tax_voucher =\
                move_line_tax.get('account_tax_voucher')
            account_tax_collected =\
                move_line_tax.get('account_tax_collected')
            amount_total_tax = move_line_tax.get('amount', 0)

            lines_tax = voucher_obj._preparate_move_line_tax(
                cr, uid,
                account_tax_voucher,  # cuenta del impuesto(account.tax)
                account_tax_collected,  # cuenta del impuesto para notas de credito/debito(account.tax)
                move_id_old, type,
                st_line.partner_id.id,
                st_line.statement_id.period_id.id,
                st_line.statement_id.journal_id.id,
                st_line.date, company_currency,
                amount_total_tax * factor,  # Monto del impuesto por el factor(cuanto le corresponde)(aml)
                amount_total_tax * factor,  # Monto del impuesto por el factor(cuanto le corresponde)(aml)
                statement_currency, False,
                move_line_tax.get('tax_id'),  # Impuesto
                move_line_tax.get('tax_analytic_id'),  # Cuenta analitica del impuesto(aml)
                amount_base_secondary,  # Monto base(aml)
                factor, context=context)
            for move_line_tax in lines_tax:
                move_line_ids.append(
                    move_line_obj.create(
                        cr, uid, move_line_tax, context=context
                        ))
        res = super(account_bank_statement_line, self).process_reconciliation(
            cr, uid, id, mv_line_dicts, context=context)
        move_line_obj.write(cr, uid, move_line_ids,
                            {'move_id': st_line.journal_entry_id.id,
                             'statement_id': st_line.statement_id.id})
        update_ok = st_line.journal_id.update_posted
        if not update_ok:
            st_line.journal_id.write({'update_posted': True})
        move_obj.button_cancel(cr, uid, [move_id_old])
        st_line.journal_id.write({'update_posted': update_ok})
        move_obj.unlink(cr, uid, move_id_old)
        return res

    def _get_factor_type(
            self, cr, uid, amount=False, ttype=False, context=None):
        '''
        This when the payment have retentiones or in refound debit/credit,
        and is used to indicate if the debit be subtracted to
        credit or credit to debit.
        1 is to debit and -1 to credit
        '''
        if context is None:
            context = {}
        factor_type = [-1, 1]
        if (amount and amount < 0) or (ttype and ttype == 'payment'):
            factor_type = [1, -1]
        context['factor_type'] = factor_type
        return True

    def _get_move_line_counterpart(self, cr, uid, mv_line_dicts, context=None):

        move_line_obj = self.pool.get('account.move.line')

        counterpart_amount = 0
        statement_amount = 0
        for move_line_dict in mv_line_dicts:

            if move_line_dict.get('counterpart_move_line_id'):
                move_counterpart_id =\
                    move_line_dict.get('counterpart_move_line_id')

                move_line_id = move_line_obj.browse(
                    cr, uid, move_counterpart_id, context=context)

                if move_line_id.journal_id.type not in (
                        'sale_refund', 'purchase_refund'):

                    statement_amount += move_line_dict.get('credit') > 0 and\
                        move_line_dict.get('credit') or\
                        move_line_dict.get('debit')

                    counterpart_amount += move_line_id.credit > 0 and\
                        move_line_id.credit or move_line_id.debit

        return [statement_amount, counterpart_amount]

    def _get_move_line_tax(self, cr, uid, mv_line_dicts, context=None):

        tax_obj = self.pool.get('account.tax')
        move_line_obj = self.pool.get('account.move.line')

        if context is None:
            context = {}

        dat = []
        factor = context.get('factor_type', [1, 1])
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
                # Validacion del debit/credit cuando la poliza contiene
                # impuesto 0 o EXENTO toma el monto base de la linea de poliza
                if not move_line_id.debit and not move_line_id.credit:
                    account_group[move_line_id.account_id.id] +=\
                        move_line_id.amount_base or 0.0
                else:
                    account_group[move_line_id.account_id.id] +=\
                        move_line_id.amount_currency or\
                        move_line_id.debit > 0 and\
                        move_line_id.debit*factor[0] or\
                        move_line_id.credit*factor[1]

        for move_account_tax in account_group:
            amount_base_secondary = 0
            tax_ids = tax_obj.search(
                cr, uid,
                [('account_collected_id', '=', move_account_tax),
                 ('tax_voucher_ok', '=', True)], limit=1)

            if tax_ids:
                tax_id = tax_obj.browse(cr, uid, tax_ids[0])

                amount_ret_tax = self._get_retention(
                    cr, uid, account_group, tax_id)
                # Validacion especial para cuando la poliza contiene impuestos
                # 0% o EXENTO en lugar de tomar debit/credit toma el monto base
                # para reporta a la DIOT validando el @amount del impuesto
                if tax_id.amount == 0:
                    amount_total_tax = 0
                    amount_base_secondary = account_group.get(move_account_tax)
                else:
                    amount_total_tax =\
                        account_group.get(move_account_tax)+amount_ret_tax

                dat.append({
                    'account_tax_voucher':
                        tax_id.account_paid_voucher_id.id,
                    'account_tax_collected':
                        tax_id.account_collected_id.id,
                    'amount': amount_total_tax,
                    'tax_id': tax_id,
                    'tax_analytic_id':
                        tax_id.account_analytic_collected_id and
                        tax_id.account_analytic_collected_id.id or False,
                    'amount_base_secondary': amount_base_secondary
                    })
        return dat

    def _get_retention(self, cr, uid, account_group=None, tax=None):
        ''' Get retention of same type of category tax
            @param account_group: Dictionary with grouped by key of account_id
                and value amount fox example {1: 1.0}
            @param tax: Object Browse of tax '''

        tax_obj = self.pool.get('account.tax')
        amount_retention_tax = 0
        if account_group and tax:
            for move_account_tax in account_group:
                if tax.amount > 0:
                    tax_ids = tax_obj.search(
                        cr, uid,
                        [('account_collected_id', '=', move_account_tax),
                         ('tax_category_id.code', '=',
                            tax.tax_category_id.code),
                         ('amount', '<', 0), ('id', '<>', tax.id),
                         ], limit=1)
                    if tax_ids:
                        amount_retention_tax += account_group[move_account_tax]

        return amount_retention_tax


class account_bank_statement(osv.osv):

    _inherit = 'account.bank.statement'

    def button_journal_entries(self, cr, uid, ids, context=None):

        aml_obj = self.pool.get('account.move.line')
        move_line_ids = []

        res = super(account_bank_statement, self).button_journal_entries(
            cr, uid, ids, context=context)

        aml_id_statement = aml_obj.search(cr, uid, res.get('domain', []))
        for move_line in aml_obj.browse(cr, uid, aml_id_statement):
            for move_id in move_line.move_id.line_id:
                move_line_ids.append(move_id.id)

        res.update({'domain': [('id', 'in', list(set(move_line_ids)))]})
        return res
