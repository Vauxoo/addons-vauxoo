# coding: utf-8
# ##########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
# ###########################################################################
#    Coded by: Rodo (rodo@vauxoo.com)
# ###########################################################################
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
# #############################################################################

from openerp.osv import osv, fields

from openerp.addons import decimal_precision as dp

import itertools


class AccountVoucher(osv.Model):
    _inherit = 'account.voucher'

    # _columns={
    # 'move_id2':fields.many2one('account.move', 'Account Entry Tax'),
    # 'move_ids2': fields.related('move_id2','line_id', type='one2many',
    # relation='account.move.line', string='Journal Items Tax', readonly=True),
    #
    # }

    def proforma_voucher(self, cr, uid, ids, context=None):
        bank_st_obj = self.pool.get('account.bank.statement.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            type_lines_mov = {'cr': [], 'dr': []}
            for line in voucher.line_dr_ids:
                if line.amount > 0.0 and line.move_line_id and\
                        line.move_line_id.move_id:
                    type_lines_mov.get('dr').append(
                        line.move_line_id.move_id)
            for line in voucher.line_cr_ids:
                if line.amount > 0.0 and line.move_line_id and\
                        line.move_line_id.move_id:
                    type_lines_mov.get('cr').append(
                        line.move_line_id.move_id)
            bank_st_obj._validate_not_refund(
                cr, uid, voucher.type, type_lines_mov, context=context)
        return super(AccountVoucher, self).proforma_voucher(
            cr, uid, ids, context=context)

    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id,
                        journal_id, currency_id, ttype, date,
                        payment_rate_currency_id,
                        company_id, context=None):
        res = super(AccountVoucher, self).onchange_amount(
            cr, uid, ids, amount, rate, partner_id, journal_id, currency_id,
            ttype, date, payment_rate_currency_id, company_id, context=context)
        res_compute = self.onchange_compute_tax(
            cr, uid, ids, res, ttype, date, context=context)
        return res_compute

    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id,
                            amount, currency_id, ttype, date, context=None):
        res = super(AccountVoucher, self).onchange_partner_id(
            cr, uid, ids, partner_id, journal_id, amount, currency_id,
            ttype, date, context=context)
        res_compute = self.onchange_compute_tax(
            cr, uid, ids, res, ttype, date, context=context)
        return res_compute

    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id,
                         partner_id, date, amount, ttype, company_id,
                         context=None):
        res = super(AccountVoucher, self).onchange_journal(
            cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date,
            amount, ttype, company_id, context=context)
        res_compute = self.onchange_compute_tax(
            cr, uid, ids, res, ttype, date, context=context)
        return res_compute

    def get_rate_line(self, cr, uid, move_line, context=None):
        if not context:
            context = {}
        for line in move_line:
            amount_base = line.debit or line.credit or 0
            rate = 1
            if amount_base and line.amount_currency:
                rate = amount_base / line.amount_currency
                return rate
        return rate

    def get_percent_pay_vs_invoice(self, cr, uid, amount_original, amount,
                                   context=None):
        return amount_original != 0 and float(amount) / float(
            amount_original) or 1.0

    def get_partial_amount_tax_pay(self, cr, uid, tax_amount, tax_base,
                                   context=None):
        return tax_amount * tax_base

    def voucher_move_line_tax_create(self, cr, uid, voucher_id, move_id,
                                     context=None):
        if context is None:
            context = {}
        bank_statement_line_obj = self.pool.get('account.bank.statement.line')
        move_line_obj = self.pool.get('account.move.line')
        cur_obj = self.pool.get('res.currency')
        object_dp = self.pool.get('decimal.precision')
        round_val = object_dp.precision_get(cr, uid, 'Account')
        company_currency = self._get_company_currency(
            cr, uid, voucher_id, context)
        current_currency = self._get_current_currency(
            cr, uid, voucher_id, context)
        move_ids = []
        move_reconcile_id = []
        context = dict(context)
        amount_tax_currency = 0.0
        for voucher in self.browse(cr, uid, [voucher_id], context=context):
            context.update({'amount_voucher': voucher.amount or 0.0})

            for line in voucher.line_ids:

                if not line.amount:
                    continue

                factor = self.get_percent_pay_vs_invoice(
                    cr, uid, line.amount_original, line.amount,
                    context=context)

                move = line.move_line_id
                mv_line_dicts = [{
                    'counterpart_move_line_id': move.id,
                    'credit': move.debit,
                    'debit': move.credit,
                    'name': move.name}]

                bank_statement_line_obj._get_factor_type(
                    cr, uid, False, voucher.type, context=context)

                context['journal_special'] = voucher.journal_id.special_journal

                dict_tax = bank_statement_line_obj._get_move_line_tax(
                    cr, uid, mv_line_dicts, context=context)

                for move_line_tax_dict in dict_tax:

                    line_tax_id = move_line_tax_dict.get('tax_id')
                    amount_base_secondary =\
                        line_tax_id.amount and\
                        line.amount_original / (1 + line_tax_id.amount) or\
                        move_line_tax_dict.get('amount_base_secondary')
                    account_tax_voucher =\
                        move_line_tax_dict.get('account_tax_voucher')
                    account_tax_collected =\
                        move_line_tax_dict.get('account_tax_collected')
                    amount_total_tax = move_line_tax_dict.get('amount', 0)

                    move_line_rec = []

                    context['date'] = voucher.date
                    reference_amount = amount_total_tax * abs(factor)

                    statement_currency_line = False
                    if current_currency != line.currency_id.id:
                        statement_currency_line = line.currency_id.id

                    if (current_currency != company_currency or
                            statement_currency_line):
                        amount_tax_currency += cur_obj.compute(
                            cr, uid,
                            statement_currency_line or current_currency,
                            company_currency,
                            reference_amount, context=context)
                    else:
                        amount_tax_currency += round(
                            reference_amount, round_val)

                    move_lines_tax = self._preparate_move_line_tax(
                        cr, uid, account_tax_voucher, account_tax_collected,
                        move_id, voucher.type, voucher.partner_id.id,
                        voucher.period_id.id, voucher.journal_id.id,
                        voucher.date, company_currency, reference_amount,
                        reference_amount, current_currency, False,
                        move_line_tax_dict.get('tax_id'),
                        move_line_tax_dict.get('tax_analytic_id'),
                        amount_base_secondary, factor,
                        statement_currency_line=statement_currency_line,
                        context=context)
                    for move_line_tax in move_lines_tax:
                        move_create = move_line_obj.create(
                            cr, uid, move_line_tax, context=context)
                        move_ids.append(move_create)
                        move_line_rec.append(move_create)

                    move_rec_exch = bank_statement_line_obj.\
                        _get_exchange_reconcile(
                            cr, uid, move_line_tax_dict, move_line_rec,
                            line.amount, line.amount_unreconciled,
                            voucher, company_currency,
                            current_currency, context=context)
                    move_reconcile_id.append(move_rec_exch[1])

            if voucher.journal_id.special_journal:
                move_line_writeoff_tax = self.writeoff_move_line_tax_get(
                    cr, uid, voucher, amount_tax_currency, move_id,
                    voucher.number, company_currency, current_currency,
                    move_reconcile_id, context=context)
                if move_line_writeoff_tax:
                    move_line_obj.create(
                        cr, uid, move_line_writeoff_tax, context=context)

        for rec_ids in move_reconcile_id:
            if len(rec_ids) >= 2:
                move_line_obj.reconcile_partial(cr, uid, rec_ids)

        return move_ids

    def writeoff_move_line_tax_get(
            self, cr, uid, voucher, line_total, move_id, name,
            company_currency, current_currency, move_reconcile_id,
            context=None):
        """Set a dict to be use to create the writeoff move line.

        :param voucher_id: Id of voucher what we are creating account_move.
        :param line_total: Amount remaining to be allocated on lines.
        :param move_id: Id of account move where this line will be added.
        :param name: Description of account move line.
        :param company_currency: id of currency of the company to which
            the voucher belong
        :param current_currency: id of currency of the voucher
        :param account_id: account_id of provision account
        :return: mapping between fieldname and value of account move line to
            create
        :rtype: dict
        """
        currency_obj = self.pool.get('res.currency')
        move_line_obj = self.pool.get('account.move.line')
        move_line = {}

        current_currency_obj = voucher.currency_id or\
            voucher.journal_id.company_id.currency_id

        if not currency_obj.is_zero(cr, uid, current_currency_obj, line_total)\
                or (company_currency == current_currency and line_total):
            sign = voucher.type in ('sale', 'receipt') and -1 or 1

            diff = line_total * sign

            aml_ids = list(itertools.chain.from_iterable(move_reconcile_id))

            # about this dcoument
            # https://docs.google.com/spreadsheets/d/1xMxmFYENGOut-8i-wHpzt-TJeyfMXXO9Kg7AD7buJ6Q/edit#gid=0https://docs.google.com/spreadsheets/d/1xMxmFYENGOut-8i-wHpzt-TJeyfMXXO9Kg7AD7buJ6Q/edit#gid=0https://docs.google.com/spreadsheets/d/1xMxmFYENGOut-8i-wHpzt-TJeyfMXXO9Kg7AD7buJ6Q/edit#gid=0
            # keep the difference of IVA in account of IVA invoiced
            # if there is not iva in invoice and then take
            # account iva of advance payment using the journal to find it
            for move_line_id in move_line_obj.browse(
                    cr, uid, aml_ids, context=context):
                if move_line_id.journal_id.type not in ('bank', 'cash'):
                    account_id = move_line_id.account_id.id
                    break
                else:
                    account_id = move_line_id.account_id.id

            move_line = {
                'name': name,
                'account_id': account_id,
                'move_id': move_id,
                'partner_id': voucher.partner_id.id,
                'date': voucher.date,
                'debit': diff > 0 and diff or 0.0,
                'credit': diff < 0 and -diff or 0.0,
                'currency_id':
                    company_currency != current_currency and
                    current_currency or False,
                'analytic_account_id':
                    voucher.analytic_id and voucher.analytic_id.id or False,
            }

        return move_line

    def _get_reconcile_tax_advance(
            self, cr, uid, voucher, move_id, context=None):

        bank_statement_line_obj = self.pool.get('account.bank.statement.line')

        company_currency = self._get_company_currency(
            cr, uid, voucher.id, context)
        statement_currency = self._get_current_currency(
            cr, uid, voucher.id, context)
        move_line_taxes = []

        for voucher_line in voucher.line_ids:
            if voucher_line.move_line_id.journal_id.type in ('cash', 'bank'):
                mv_line_dicts = [{
                    'counterpart_move_line_id': voucher_line.move_line_id.id,
                    'credit': voucher_line.amount,
                    'debit': 0}]
                move_line_taxes =\
                    bank_statement_line_obj.create_move_line_tax_payment(
                        cr, uid, mv_line_dicts, voucher.partner_id.id,
                        voucher.period_id.id, voucher.journal_id.id,
                        voucher.date, voucher.type, voucher, company_currency,
                        statement_currency, move_id=move_id, context=context)

        return move_line_taxes

    # pylint: disable=W0622
    def _preparate_move_line_tax(self, cr, uid, src_account_id,
                                 dest_account_id, move_id, type, partner,
                                 period, journal, date, company_currency,
                                 reference_amount, amount_tax_unround,
                                 reference_currency_id, tax_id,
                                 line_tax, acc_a,
                                 # informacion de lineas de impuestos
                                 amount_base_tax,
                                 factor=0, statement_currency_line=None,
                                 context=None):

        account_collected_id = dest_account_id

        if type == 'payment' or reference_amount < 0:
            src_account_id, dest_account_id = dest_account_id, src_account_id
        if type == 'payment' and reference_amount < 0:
            src_account_id, dest_account_id = dest_account_id, src_account_id

        reference_currency_id = statement_currency_line or\
            reference_currency_id

        amount_base, tax_secondary = self._get_base_amount_tax_secondary(
            cr, uid, line_tax, amount_base_tax * factor, reference_amount,
            context=context)

        amount_tax_sec = 0
        if tax_secondary:
            amount_tax_sec = self.pool.get('account.tax').browse(
                cr, uid, tax_secondary, context=context).amount

        debit_line_vals = {
            'name': line_tax.name,
            'quantity': 1,
            'partner_id': partner,
            'debit': abs(reference_amount),
            'credit': 0.0,
            'account_id': dest_account_id,
            'journal_id': journal,
            'period_id': period,
            'move_id': move_id and int(move_id) or None,
            'tax_id': tax_id,
            'is_tax_voucher': True,
            'analytic_account_id': acc_a,
            'date': date,
            'tax_voucher_id': tax_id,
        }
        credit_line_vals = {
            'name': line_tax.name,
            'quantity': 1,
            'partner_id': partner,
            'debit': 0.0,
            'credit': abs(reference_amount),
            'account_id': src_account_id,
            'journal_id': journal,
            'period_id': period,
            'move_id': move_id and int(move_id) or None,
            'amount_tax_unround': amount_tax_unround,
            'tax_id': tax_id,
            'is_tax_voucher': True,
            'analytic_account_id': acc_a,
            'date': date,
            'tax_voucher_id': tax_id,
        }

        if context.get('amount_voucher') and context.get('amount_voucher') < 0:
            debit_line_vals.update(
                {'credit': debit_line_vals.get('debit', 0.0), 'debit': 0.0})
            credit_line_vals.update(
                {'debit': credit_line_vals.get('credit', 0.0), 'credit': 0.0})

        if type in ('payment', 'purchase'):
            if reference_amount < 0:
                credit_line_vals.pop('analytic_account_id')
                credit_line_vals.update({
                    'amount_base': abs(amount_base),
                    'tax_id_secondary': tax_secondary})
            else:
                debit_line_vals.pop('analytic_account_id')
                debit_line_vals.update({
                    'tax_id_secondary': tax_secondary,
                    'amount_base': abs(amount_base)})
        else:
            if reference_amount < 0:
                debit_line_vals.pop('analytic_account_id')
            else:
                credit_line_vals.pop('analytic_account_id')

        if not amount_tax_unround:
            credit_line_vals.pop('amount_tax_unround')
            credit_line_vals.pop('tax_id')
            debit_line_vals.pop('tax_id')
            credit_line_vals.pop('is_tax_voucher')
            debit_line_vals.pop('is_tax_voucher')

        account_obj = self.pool.get('account.account')
        cur_obj = self.pool.get('res.currency')

        reference_amount = abs(reference_amount)
        src_acct, dest_acct = account_obj.browse(
            cr, uid, [src_account_id, dest_account_id], context=context)
        src_main_currency_id = src_acct.currency_id\
            and src_acct.currency_id.id\
            or src_acct.company_id.currency_id.id
        dest_main_currency_id = dest_acct.currency_id\
            and dest_acct.currency_id.id or dest_acct.company_id.currency_id.id

        # get rate of bank statement if rate is different to currency
        if context.get('st_line_currency_rate') and\
                statement_currency_line != company_currency:
            credit_line_vals['credit'] = cur_obj.round(
                cr, uid, src_acct.company_id.currency_id,
                reference_amount / context.get('st_line_currency_rate'))
            debit_line_vals['debit'] = cur_obj.round(
                cr, uid, src_acct.company_id.currency_id,
                reference_amount / context.get('st_line_currency_rate'))
            if amount_tax_sec:
                debit_line_vals['amount_base'] = cur_obj.round(
                    cr, uid, src_acct.company_id.currency_id,
                    abs(amount_base) / context.get('st_line_currency_rate'))
        else:
            if reference_currency_id != src_main_currency_id:
                # fix credit line:
                credit_line_vals['credit'] = cur_obj.compute(
                    cr, uid, reference_currency_id, src_main_currency_id,
                    reference_amount, context=context)

            if reference_currency_id != dest_main_currency_id:
                # fix debit line:
                debit_line_vals['debit'] = cur_obj.compute(
                    cr, uid, reference_currency_id, dest_main_currency_id,
                    reference_amount, context=context)
                if amount_tax_sec:
                    debit_line_vals['amount_base'] = cur_obj.compute(
                        cr, uid, reference_currency_id, dest_main_currency_id,
                        abs(amount_base), context=context)

        if reference_currency_id != company_currency:
            debit_line_vals.update(
                currency_id=reference_currency_id,
                amount_currency=reference_amount)
            credit_line_vals.update(
                currency_id=reference_currency_id,
                amount_currency=-reference_amount)

        if self.pool.get('account.journal').browse(
                cr, uid, journal).special_journal:
            return [
                account_collected_id == debit_line_vals.get('account_id') and
                debit_line_vals or credit_line_vals]

        return [debit_line_vals, credit_line_vals]

    def _get_base_amount_tax_secondary(self, cr, uid, line_tax,
                                       amount_base_tax, reference_amount,
                                       context=None):
        amount_base = 0
        tax_secondary = False
        if line_tax and line_tax.tax_category_id\
                and line_tax.tax_category_id.name in \
                ('IVA', 'IVA-EXENTO', 'IVA-RET', 'IVA-PART'):
            amount_base = line_tax.amount and\
                reference_amount / line_tax.amount or amount_base_tax
            tax_secondary = line_tax.id
        return [amount_base, tax_secondary]

    def action_move_line_create(self, cr, uid, ids, context=None):
        res = super(AccountVoucher, self).action_move_line_create(
            cr, uid, ids, context=context)
        for acc_voucher in self.browse(cr, uid, ids, context=context):
            self.voucher_move_line_tax_create(
                cr, uid, acc_voucher.id, acc_voucher.move_id.id,
                context=context)
        return res

    def onchange_compute_tax(self, cr, uid, ids, lines=None, ttype=False,
                             date=False, context=None):
        if context is None:
            context = {}
        context = dict(context)
        move_obj = self.pool.get('account.move.line')
        absl_obj = self.pool.get('account.bank.statement.line')
        lines_ids = []
        if lines and lines.get('value', False):
            lines_ids.extend(lines['value'].get('line_cr_ids', []))
            lines_ids.extend(lines['value'].get('line_dr_ids', []))
            for line in lines_ids:
                if isinstance(line, tuple):
                    continue
                factor = self.get_percent_pay_vs_invoice(cr, uid, line[
                    'amount_original'], line['amount'], context=context)
                list_tax = []
                if line['amount'] > 0:
                    move = move_obj.browse(
                        cr, uid, line['move_line_id'],
                        context=context)
                    mv_line_dicts = [{
                        'counterpart_move_line_id': move.id,
                        'credit': move.debit,
                        'debit': move.credit,
                        'name': move.name}]
                    absl_obj._get_factor_type(
                        cr, uid, False, ttype, context=context)
                    dict_tax = absl_obj._get_move_line_tax(
                        cr, uid, mv_line_dicts, context=context)
                    for tax in dict_tax:
                        if tax:
                            tax_br = tax.get('tax_id', False)
                            base_amount = tax.get('amount', 0.0)
                            account = tax.get('account_tax_collected', False)
                            credit_amount = float('%.*f' % (2, (
                                base_amount * factor)))
                            credit_amount_original = (base_amount * factor)
                            amount_unround = float(base_amount * factor)
                            base_amount_curr = base_amount
                            move_line_id = tax.get('move_line_reconcile')
                            list_tax.append([
                                0, False, {
                                    'tax_id': tax_br.id,
                                    'account_id': account,
                                    'amount_tax': credit_amount_original,
                                    'amount_tax_unround': amount_unround,
                                    'tax': credit_amount,
                                    'original_tax': base_amount_curr,
                                    'move_line_id': move_line_id[0],
                                    'analytic_account_id': tax.get(
                                        'tax_analytic_id', False),
                                    'amount_base': tax.get(
                                        'amount_base_secondary', 0.0)}])
                lista_tax_to_add = [[5, False, False]]
                for tax in list_tax:
                    lista_tax_to_add.append(tax)
                line.update({'tax_line_ids': lista_tax_to_add})
        return lines

    def _get_retention_voucher(self, cr, uid, invoice=None, tax=None):
        invoice_obj = self.pool.get('account.invoice')
        amount_retention_tax = 0
        for inv in invoice_obj.browse(cr, uid, [invoice.id]):
            for tax_inv in inv.tax_line:
                if tax.amount > 0:
                    if tax_inv.tax_id.tax_category_id.code ==\
                        tax.tax_id.tax_category_id.code and\
                            tax_inv.tax_id.amount < 0:

                        amount_retention_tax += tax_inv.amount
        return amount_retention_tax


class AccountVoucherLine(osv.Model):
    _inherit = 'account.voucher.line'

    def onchange_amount(self, cr, uid, ids, amount=False,
                        amount_unreconciled=False, context=None,
                        voucher_id=False, move_line_id=False,
                        amount_original=False):
        if not context:
            context = {}
        context = dict(context)
        voucher_obj = self.pool.get('account.voucher')
        move_obj = self.pool.get('account.move.line')
        absl_obj = self.pool.get('account.bank.statement.line')
        factor = voucher_obj.get_percent_pay_vs_invoice(
            cr, uid, amount_original, amount, context=context)
        res = super(AccountVoucherLine, self).onchange_amount(
            cr, uid, ids, amount, amount_unreconciled)
        if not voucher_id and not move_line_id and not amount_original:
            return res
        if amount > 0:
            list_tax = []
            move = move_obj.browse(cr, uid, move_line_id, context=context)
            mv_line_dicts = [{
                'counterpart_move_line_id': move.id,
                'credit': move.debit,
                'debit': move.credit,
                'name': move.name}]
            absl_obj._get_factor_type(
                cr, uid, False, context.get('type', False), context=context)
            dict_tax = absl_obj._get_move_line_tax(
                cr, uid, mv_line_dicts, context=context)
            for tax in dict_tax:
                if tax:
                    tax_br = tax.get('tax_id', False)
                    base_amount = tax.get('amount', 0.0)
                    account = tax.get('account_tax_collected', False)
                    credit_amount = float('%.*f' % (2, (
                        base_amount * factor)))
                    credit_amount_original = (base_amount * factor)
                    amount_unround = float(base_amount * factor)
                    base_amount_curr = base_amount
                    move_line_id = tax.get('move_line_reconcile')
                    list_tax.append([
                        0, False, {
                            'tax_id': tax_br.id,
                            'account_id': account,
                            'amount_tax': credit_amount_original,
                            'amount_tax_unround': amount_unround,
                            'tax': credit_amount,
                            'original_tax': base_amount_curr,
                            'move_line_id': move_line_id[0],
                            'analytic_account_id': tax.get(
                                'tax_analytic_id', False),
                            'amount_base': tax.get(
                                'amount_base_secondary', 0.0)}])
            lista_tax_to_add = [[5, False, False]]
            for tax in list_tax:
                lista_tax_to_add.append(tax)
            res['value'].update({'tax_line_ids': lista_tax_to_add})
        return res

    _columns = {
        'tax_line_ids': fields.one2many(
            'account.voucher.line.tax', 'voucher_line_id', 'Tax Lines'),
    }


class AccountMoveLine(osv.Model):
    _inherit = 'account.move.line'

    def _get_round(self, cr, uid, ids, context=None):

        if context is None:
            context = {}

        if context.get('apply_round', False):
            dat = []
        else:
            dat = self._get_query_round(cr, uid, ids, context=context)
        res_round = {}
        res_without_round = {}
        res_ids = {}
        object_dp = self.pool.get('decimal.precision')
        round_val = object_dp.precision_get(cr, uid, 'Account')
        for val_round in dat:
            res_round.setdefault(val_round['account_id'], 0)
            res_without_round.setdefault(val_round['account_id'], 0)
            res_ids.setdefault(val_round['account_id'], 0)
            res_round[val_round['account_id']] += \
                round(val_round['round'], round_val)
            res_without_round[val_round['account_id']] += val_round['without']
            res_ids[val_round['account_id']] = val_round['id']
        for res_diff_id in res_round.items():
            diff_val = \
                abs(res_without_round[res_diff_id[0]]) -\
                abs(res_round[res_diff_id[0]])
            diff_val = round(diff_val, round_val)
            if diff_val != 0.00:
                move_diff_id = [res_ids[res_diff_id[0]]]
                for move in self.browse(
                        cr, uid, move_diff_id, context=context):
                    move_line_ids = self.search(
                        cr, uid,
                        [('move_id', '=', move.move_id.id),
                         ('is_tax_voucher', '=', True)])
                    for diff_move in self.browse(
                            cr, uid, move_line_ids, context=context):
                        if diff_move.debit == 0.0 and diff_move.credit\
                                and diff_move.credit + diff_val:
                            self._write(
                                cr, uid, [diff_move.id],
                                {'credit': diff_move.credit + diff_val})
                        if diff_move.credit == 0.0 and diff_move.debit\
                                and diff_move.debit + diff_val:
                            self._write(
                                cr, uid, [diff_move.id],
                                {'debit': diff_move.debit + diff_val})
        return True

    def _get_query_round(self, cr, uid, ids, context=None):
        if context is None:
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
                order by id asc """, (tuple(ids),))
        dat = cr.dictfetchall()
        return dat

    # pylint: disable=W0622
    # commented because that has an error with bank statement
    def reconcile(self, cr, uid, ids, type='auto', writeoff_acc_id=False,
                  writeoff_period_id=False, writeoff_journal_id=False,
                  context=None):
        res = super(AccountMoveLine, self).reconcile(
            cr, uid, ids=ids, type='auto', writeoff_acc_id=writeoff_acc_id,
            writeoff_period_id=writeoff_period_id,
            writeoff_journal_id=writeoff_journal_id, context=context)
        return res

    _columns = {
        'amount_tax_unround': fields.float(
            'Amount tax undound', digits=(12, 16)),
        'tax_id': fields.many2one('account.voucher.line.tax', 'Tax'),
        'tax_voucher_id': fields.many2one(
            'account.voucher.line.tax', 'Tax Voucher'),
        'is_tax_voucher': fields.boolean('Tax voucher')
    }


class AccountVoucherLineTax(osv.Model):
    _name = 'account.voucher.line.tax'

    def _compute_balance(self, cr, uid, ids, name, args, context=None):
        res = {}

        for line_tax in self.browse(cr, uid, ids, context=context):
            tax_sum = 0.0
            old_ids = self.search(
                cr, uid, [('move_line_id', '=', line_tax.move_line_id.id),
                          ('id', '!=', line_tax.id)])
            for lin_sum in self.browse(cr, uid, old_ids, context=context):
                tax_sum += lin_sum.amount_tax
            res[line_tax.id] = line_tax.original_tax - tax_sum
        return res

    def onchange_amount_tax(self, cr, uid, ids, amount, tax):
        res = {}
        res['value'] = {'amount_tax': amount, 'amount_tax_unround': amount,
                        'diff_amount_tax': abs(tax - amount)}
        return res

    _columns = {
        'tax_id': fields.many2one('account.tax', 'Tax'),
        'account_id': fields.many2one('account.account', 'Account'),
        'amount_tax': fields.float('Amount Tax', digits=(12, 16)),
        'amount_tax_unround': fields.float('Amount tax undound'),
        'original_tax': fields.float('Original Import Tax'),
        'tax': fields.float('Tax'),
        'balance_tax': fields.function(
            _compute_balance, type='float', string='Balance Import Tax',
            store=True, digits=(12, 6)),
        # 'balance_tax':fields.float('Balance Import Tax'),
        'diff_amount_tax': fields.float(
            'Difference', digits_compute=dp.get_precision('Account')),
        'diff_account_id': fields.many2one('account.account', 'Account Diff'),
        'voucher_line_id': fields.many2one(
            'account.voucher.line', 'Voucher Line'),
        'move_line_id': fields.many2one('account.move.line', 'Move'),
        'analytic_account_id': fields.many2one(
            'account.analytic.account', 'Account Analytic'),
        'amount_base': fields.float('Amount Base')
    }
