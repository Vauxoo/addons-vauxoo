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
import time
from openerp.osv import fields, osv
from openerp import netsvc
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class hr_expense_expense(osv.Model):
    _inherit = "hr.expense.expense"
    _columns =  {
            'fully_applied_vat':fields.boolean('Fully Applied VAT',
                help=('Indicates if VAT has been computed in this expense')), 
            }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'fully_applied_vat': False,
                        })
        return super(hr_expense_expense, self).copy(cr, uid, id, default,
                        context=context)
    def payment_reconcile(self, cr, uid, ids, context=None):
        """ It reconcile the expense advance and expense invoice account move
        lines.
        """
        context = context or {}
        res = super(hr_expense_expense, self).payment_reconcile(cr, uid, ids,
                                                            context=context)
        self.create_her_tax(cr, uid, ids, res, context=context)
        return res

    def create_her_tax(self, cr, uid, ids, aml={}, context=None):
        aml_obj = self.pool.get('account.move.line')
        context = context or {}
        ids= isinstance(ids,(int,long)) and [ids] or ids
        exp = self.browse(cr, uid, ids, context=context)[0]
        if exp.fully_applied_vat:
            return True
        for invoice in exp.invoice_ids:
            for tax in invoice.tax_line:
                if tax.tax_id.tax_voucher_ok:
                    account_id = tax.tax_id.account_collected_voucher_id.id
                    amount = -tax.amount
                    move_line_tax = self.preparate_move_line_tax(exp, tax,
                                        account_id, amount, context=context)
                    aml_obj.create(cr, uid, move_line_tax, context=context)
                    
                    account_id = tax.tax_id.account_collected_id.id
                    amount = tax.amount
                    move_line_tax2 = self.preparate_move_line_tax(exp, tax,
                                        account_id, amount, context=context)
                    aml_obj.create(cr, uid, move_line_tax2, context=context)
        exp.write({'fully_applied_vat':True})
        return True
    
    def preparate_move_line_tax(self, exp, tax, acc, amount, context=None):
        return  {
                'journal_id': exp.account_move_id.journal_id.id,
                'period_id': exp.account_move_id.period_id.id,
                'name': tax.name,
                'account_id': acc,
                'move_id': exp.account_move_id.id,
                #'amount_currency': 0.0,
                #'partner_id': ,
                #'currency_id': exp.currency_id.id,
                'quantity': 1,
                'debit': amount < 0 and -amount or 0.0,
                'credit': amount > 0 and amount or 0.0,
                'date': exp.account_move_id.date,
                }
