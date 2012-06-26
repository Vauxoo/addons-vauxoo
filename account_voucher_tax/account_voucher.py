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
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        invoice_obj = self.pool.get('account.invoice')
        res=super(account_voucher, self).voucher_move_line_create(cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None)
        for voucher in self.browse(cr,uid,[voucher_id],context=context):
            lineas=[]
            for line in voucher.line_ids:
                if line.amount>0:
                    invoice_id=invoice_obj.search(cr,uid,[('number','=',line.name)],context=context)
                    for invoice in invoice_obj.browse(cr,uid,invoice_id,context=context):
                        for tax in invoice.tax_line:
                            if tax.tax_id.tax_voucher_ok:
                                account=tax.tax_id.account_collected_voucher_id.id
                                if invoice.type=='out_invoice':
                                    account=tax.tax_id.account_paid_voucher_id.id
                                monto_credit=(tax.tax_id.amount*tax.base)*(line.amount/line.amount_original)
                                monto_debit=0.0
                                if tax.tax_id.amount<0:
                                    monto_credit=0.0
                                    monto_debit=-1.0*(tax.tax_id.amount*tax.base)*(line.amount/line.amount_original)
                                
                                lineas.append({
                                    'journal_id': voucher.journal_id.id,
                                    'period_id': voucher.period_id.id,
                                    'name': tax.name or '/',
                                    'account_id': tax.account_id.id,
                                    'move_id': move_id,
                                    'partner_id': voucher.partner_id.id,
                                    'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                                    'quantity': 1,
                                    'credit': monto_credit,
                                    'debit': monto_debit,
                                    'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                                    'date': voucher.date
                                })
                                lineas.append({
                                    'journal_id': voucher.journal_id.id,
                                    'period_id': voucher.period_id.id,
                                    'name': tax.name or '/',
                                    'account_id': account,
                                    'move_id': move_id,
                                    'partner_id': voucher.partner_id.id,
                                    'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                                    'quantity': 1,
                                    'credit': monto_debit,
                                    'debit': monto_credit,
                                    'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                                    'date': voucher.date
                                })
            for move_line in lineas:
                move_line_obj.create(cr,uid,move_line,context=context)
        return res
account_voucher()


