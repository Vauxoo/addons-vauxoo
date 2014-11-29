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


class account_bank_statement_line(osv.osv):

    _inherit = 'account.bank.statement.line'

    def process_reconciliation(self, cr, uid, id, mv_line_dicts, context=None):

        if context is None:
            context = {}

        move_obj = self.pool.get('account.move.line')
        invoice_obj = self.pool.get('account.invoice')
        acc_voucher_obj = self.pool.get('account.voucher')
        move_line_ids = []

        st_line = self.browse(cr, uid, id, context=context)
        company_currency = st_line.journal_id.company_id.currency_id.id
        statement_currency = st_line.journal_id.currency.id or company_currency

        for mv_line_dict in mv_line_dicts:
            print mv_line_dict,"mv_line_dict"
            if mv_line_dict.get('counterpart_move_line_id'):
                move_line_id = mv_line_dict.get('counterpart_move_line_id')
                move_id = move_obj.browse(
                        cr, uid, move_line_id, context=context).move_id.id
                invoice_ids = invoice_obj.search(
                        cr, uid, [('move_id', '=', move_id)], context=context)
                print invoice_ids,"invoice_ids"
                for invoice in invoice_obj.browse(cr, uid, invoice_ids, context=context):
                    for tax in invoice.tax_line:
                        if tax.tax_id.tax_voucher_ok:
                            account_tax_voucher = tax.tax_id.account_paid_voucher_id.id
                            account_tax_collected = tax.tax_id.account_collected_id.id
                            amount_original_inv = invoice.amount_total
                            amount_statement_bank = st_line.amount
                            type = 'sale'
                            if st_line.amount > invoice.amount_total:
                                amount_statement_bank = invoice.amount_total
                            if st_line.amount < 0:
                                type = 'payment'
                                amount_statement_bank = amount_statement_bank * -1

                            factor = acc_voucher_obj.get_percent_pay_vs_invoice(cr, uid,
                                amount_original_inv , amount_statement_bank, context=context)
                            move_lines_tax = acc_voucher_obj.\
                                _preparate_move_line_tax(cr, uid,
                                account_tax_voucher,
                                account_tax_collected, None,
                                type, invoice.partner_id.id,
                                st_line.statement_id.period_id.id,
                                st_line.statement_id.journal_id.id,
                                st_line.date, company_currency,
                                tax.amount * factor, tax.amount * factor,
                                statement_currency,
                                False, tax.tax_id, tax.account_analytic_id and
                                    tax.account_analytic_id.id or False,
                                tax.base_amount, factor, context=context)

                            for move_line_tax in move_lines_tax:
                                    move_line_ids.append(
                                        move_obj.create(cr, uid, move_line_tax,
                                                            context=context))

        res = super(account_bank_statement_line, self).process_reconciliation(cr, uid, id, mv_line_dicts, context=context)
        move_obj.write(cr, uid, move_line_ids, {'move_id': st_line.journal_entry_id.id})
        return res
