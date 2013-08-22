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
from openerp.osv import fields 

class account_reconcile_advance(osv.Model):
    _inherit = 'account.reconcile.advance'
    
    def payment_reconcile(self, cr, uid, ids, context=None):
        res = super(account_reconcile_advance,
                        self).payment_reconcile(cr, uid, ids, context=context)
        self.create_ara_tax(cr, uid, ids, context=context)
        return resq

    def create_ara_tax(self, cr, uid, ids, context=None):
        acc_voucher_obj = self.pool.get('account.voucher')
        adv = self.browse(cr, uid, ids, context=context)[0]
        for invoice in adv.invoice_ids:
            print invoice.amount_total,'imprimo amount_total'
            for tax in invoice.tax_line:
                if tax.tax_id.tax_voucher_ok:
                    account_tax_voucher = tax.tax_id.account_paid_voucher_id.id
                    account_tax_collected = tax.tax_id.account_collected_id.id
                    print tax.tax_id.name,'imprimo tame'
                    factor = acc_voucher_obj.get_percent_pay_vs_invoice(cr, uid,
                        invoice.amount_total, 58, context=context)
                    print factor,'imprimo factor'
                    print tax.amount * factor,'amount'
                    move_lines_tax = acc_voucher_obj.\
                                            _preparate_move_line_tax(cr, uid,
                        account_tax_voucher,
                        account_tax_collected, exp.account_move_id.id,
                        'payment', invoice.partner_id.id,
                        adv.account_move_id.period_id.id,
                        adv.account_move_id.journal_id.id,
                        adv.account_move_id.date, company_currency,
                        tax.amount, tax.amount,
                        current_currency,
                        False, adv.name, adv.account_analytic_id and\
                            adv.account_analytic_id.id or False,
                        adv.base_amount, factor, context=context)
                        
                    for move_line_tax in move_lines_tax:
                        move_create = aml_obj.create(cr ,uid, move_line_tax,
                                                context=context)
        return True

