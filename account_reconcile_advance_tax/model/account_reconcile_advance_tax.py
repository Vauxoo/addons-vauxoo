#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Julio Cesar Serna Hernandez(julio@vauxoo.com)
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

from openerp.osv import osv


class account_reconcile_advance(osv.Model):
    _inherit = 'account.reconcile.advance'

    def payment_reconcile(self, cr, uid, ids, context=None):
        res = super(account_reconcile_advance,
                    self).payment_reconcile(cr, uid, ids, context=context)
        self.create_ara_tax(cr, uid, ids, amount_inv_pay=res, context=context)
        return res

    def _get_company_currency(self, cr, uid, adv_id, context=None):
        return self.pool.get('account.reconcile.advance').browse(cr,
            uid, adv_id,
            context).move_id.journal_id.company_id.currency_id.id

    def _get_current_currency(self, cr, uid, exp_id, context=None):
        exp = self.pool.get('account.reconcile.advance').browse(cr, uid, adv_id,
                                                                context)
        return exp.currency_id.id or\
            self._get_company_currency(cr, uid, adv_id, context)

    def create_ara_tax(self, cr, uid, ids, amount_inv_pay={}, context=None):
        aml_obj = self.pool.get('account.move.line')
        acc_voucher_obj = self.pool.get('account.voucher')
        adv = self.browse(cr, uid, ids, context=context)[0]

        company_currency = self._get_company_currency(cr, uid,
                            adv.id, context)

        current_currency = self._get_company_currency(cr, uid,
                            adv.id, context)

        for invoice in adv.invoice_ids:
            for tax in invoice.tax_line:
                if tax.tax_id.tax_voucher_ok:

                    account_tax_voucher = tax.tax_id.account_paid_voucher_id.id
                    account_tax_collected = tax.tax_id.account_collected_id.id

                    factor = acc_voucher_obj.get_percent_pay_vs_invoice(cr,
                                uid, invoice.amount_total,
                                amount_inv_pay.get(invoice.id, 0.0),
                        context=context)

                    move_lines_tax = acc_voucher_obj.\
                        _preparate_move_line_tax(cr, uid,
                        account_tax_voucher, account_tax_collected,
                        adv.move_id.id, 'payment', invoice.partner_id.id,
                        adv.move_id.period_id.id, adv.move_id.journal_id.id,
                        adv.move_id.date, company_currency,
                        tax.amount * factor, tax.amount * factor,
                        current_currency, False, tax.tax_id,
                        tax.account_analytic_id and
                            tax.account_analytic_id.id or False,
                        tax.base_amount, factor, context=context)

                    for move_line_tax in move_lines_tax:
                        move_create = aml_obj.create(cr, uid, move_line_tax,
                                                context=context)
        return True
