# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
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
from openerp.osv import fields, osv

class account_voucher(osv.Model):
    _inherit = 'account.voucher'
    
    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id,\
        amount, currency_id, ttype, date, context=None):
        if context is None:
            context = {}
        acc_move_line_obj = self.pool.get('account.move.line')
        acc_invoice_obj = self.pool.get('account.invoice')
        res = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id,\
            journal_id, amount, currency_id, ttype, date, context=context)
        values = res.get('value', {})
        if values.get('line_cr_ids', False) and ttype == 'payment':
            for line in values.get('line_cr_ids'):
                acc_line = line.get('move_line_id', False)
                move_id = acc_line and acc_move_line_obj.browse(cr, uid, acc_line,\
                    context=context).move_id or False
                invoice_line = move_id and acc_invoice_obj.search(cr, uid, [\
                    ('move_id', '=', move_id.id)], context=context) or False
                if invoice_line:
                    line.update({'reconcile' : False, 'line_to_invoice' : True})
        if values.get('line_dr_ids', False) and ttype == 'receipt':
            for line in values.get('line_dr_ids'):
                acc_line = line.get('move_line_id', False)
                move_id = acc_line and acc_move_line_obj.browse(cr, uid, acc_line,\
                    context=context).move_id or False
                invoice_line = move_id and acc_invoice_obj.search(cr, uid, [\
                    ('move_id', '=', move_id.id)], context=context) or False
                if invoice_line:
                    line.update({'reconcile' : False, 'line_to_invoice' : True})
        return res
        
    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id,\
        ttype, date, payment_rate_currency_id, company_id, context=None):
        if context is None:
            context = {}
        acc_move_line_obj = self.pool.get('account.move.line')
        acc_invoice_obj = self.pool.get('account.invoice')
        res = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id,\
            journal_id, amount, currency_id, ttype, date, context=context)
        values = res.get('value', {})
        if values.get('line_cr_ids', False) and ttype == 'payment':
            for line in values.get('line_cr_ids'):
                acc_line = line.get('move_line_id', False)
                move_id = acc_line and acc_move_line_obj.browse(cr, uid, acc_line,\
                    context=context).move_id or False
                invoice_line = move_id and acc_invoice_obj.search(cr, uid, [\
                    ('move_id', '=', move_id.id)], context=context) or False
                if invoice_line:
                    line.update({'reconcile' : False, 'line_to_invoice' : True})
        if values.get('line_dr_ids', False) and ttype == 'receipt':
            for line in values.get('line_dr_ids'):
                acc_line = line.get('move_line_id', False)
                move_id = acc_line and acc_move_line_obj.browse(cr, uid, acc_line,\
                    context=context).move_id or False
                invoice_line = move_id and acc_invoice_obj.search(cr, uid, [\
                    ('move_id', '=', move_id.id)], context=context) or False
                if invoice_line:
                    line.update({'reconcile' : False, 'line_to_invoice' : True})
        return res
        
    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id,\
        partner_id, date, amount, ttype, company_id, context=None):
        if context is None:
            context = {}
        acc_move_line_obj = self.pool.get('account.move.line')
        acc_invoice_obj = self.pool.get('account.invoice')
        res = super(account_voucher, self).onchange_journal(cr, uid, ids, journal_id, line_ids,\
            tax_id, partner_id, date, amount, ttype, company_id, context=context)
        values = res.get('value', {})
        if values.get('line_cr_ids', False) and ttype == 'payment':
            for line in values.get('line_cr_ids'):
                acc_line = line.get('move_line_id', False)
                move_id = acc_line and acc_move_line_obj.browse(cr, uid, acc_line,\
                    context=context).move_id or False
                invoice_line = move_id and acc_invoice_obj.search(cr, uid, [\
                    ('move_id', '=', move_id.id)], context=context) or False
                if invoice_line:
                    line.update({'reconcile' : False, 'line_to_invoice' : True})
        if values.get('line_dr_ids', False) and ttype == 'receipt':
            for line in values.get('line_dr_ids'):
                acc_line = line.get('move_line_id', False)
                move_id = acc_line and acc_move_line_obj.browse(cr, uid, acc_line,\
                    context=context).move_id or False
                invoice_line = move_id and acc_invoice_obj.search(cr, uid, [\
                    ('move_id', '=', move_id.id)], context=context) or False
                if invoice_line:
                    line.update({'reconcile' : False, 'line_to_invoice' : True})
        return res
    
class account_voucher_line(osv.Model):
    _inherit = 'account.voucher.line'
    
    _columns = {
        'line_to_invoice': fields.boolean('Line to Invoice', help='If this field is true indicates'\
            ' that this line coming from an invoice refound')
    }
