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
    
    def get_cr_dr(self, cr, uid, ids, line, context=None):
        acc_move_line_obj = self.pool.get('account.move.line')
        acc_invoice_obj = self.pool.get('account.invoice')
        
        acc_line = line.get('move_line_id', False)
        move_exclude = False
        move_id = acc_line and acc_move_line_obj.browse(cr, uid, acc_line,\
            context=context).move_id or False
        invoice_line = move_id and acc_invoice_obj.search(cr, uid, [\
            ('move_id', '=', move_id.id)], context=context) or False
        if invoice_line:
            line.update({'reconcile' : False, 'line_to_invoice' : True, 'amount': 0})
            move_exclude = acc_line
        return move_exclude
    
    def move_include(self, cr, uid, values, val_exclude, context=None):
        print values,'valuesvaluesvalues'
        value_cr = [val_cr.get('move_line_id', False) for val_cr in values.get('line_cr_ids', {})]
        value_dr = [val_dr.get('move_line_id', False) for val_dr in values.get('line_dr_ids', {})]
        return list(set(value_cr + value_dr) - set(val_exclude))
    
    def recompute_moves(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, values, move_exclude, context=None):
        print values,'values'
        move_include = self.move_include(cr, uid, values, move_exclude, context=context)
        context['move_line_ids'] = move_include
        result = self.recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=context)
        values_new = result.get('value', {})
        
        for val_cr in values.get('line_cr_ids', {}):
            val_cr.update({'amount': line['amount'] for line in values_new.get('line_cr_ids') if line['move_line_id'] == val_cr['move_line_id']})
        for val_dr in values.get('line_dr_ids', {}):
            val_dr.update({'amount': line['amount'] for line in values_new.get('line_dr_ids') if line['move_line_id'] == val_dr['move_line_id']})
        return True
    
    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id,\
        amount, currency_id, ttype, date, context=None):
        if context is None:
            context = {}
        res = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id,\
            journal_id, amount, currency_id, ttype, date, context=context)
        values = res.get('value', {})
        if values.get('line_cr_ids', False) and ttype == 'payment' and amount>=0:
                move_include1 = [
                    self.get_cr_dr(cr, uid, ids, line, context=context)
                    for line in values.get('line_cr_ids') ]
        if values.get('line_dr_ids', False) and ttype == 'receipt' and amount>=0:
                move_include2 = [
                    self.get_cr_dr(cr, uid, ids, line, context=context)
                    for line in values.get('line_dr_ids') ]
        return res
        
    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id,\
        ttype, date, payment_rate_currency_id, company_id, context=None):
        if context is None:
            context = {}
        res = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id,\
            journal_id, amount, currency_id, ttype, date, context=context)
        values = res.get('value', {})
        if values.get('line_cr_ids', False) and ttype == 'payment':
            for line in values.get('line_cr_ids'):
                self.get_cr_dr(cr, uid, ids, line, context=context)
        if values.get('line_dr_ids', False) and ttype == 'receipt':
            for line in values.get('line_dr_ids'):
                self.get_cr_dr(cr, uid, ids, line, context=context)
        return res
        
    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id,\
        partner_id, date, amount, ttype, company_id, context=None):
        if context is None:
            context = {}
        res = super(account_voucher, self).onchange_journal(cr, uid, ids, journal_id, line_ids,\
            tax_id, partner_id, date, amount, ttype, company_id, context=context)
        print res
        values = res and res.get('value', {}) or {}
        move_exclude = []
        if values.get('line_cr_ids', False) and ttype == 'payment' and amount>=0:
            move_exclude = [
                self.get_cr_dr(cr, uid, ids, line, context=context)
                for line in values.get('line_cr_ids') ]
        if values.get('line_dr_ids', False) and ttype == 'receipt' and amount>=0:
            move_exclude = [
                self.get_cr_dr(cr, uid, ids, line, context=context)
                for line in values.get('line_dr_ids') ]
                
        self.recompute_moves(cr, uid, ids, partner_id, journal_id, amount, values.get('currency_id', False), ttype, date, values, move_exclude, context=context)
            
        return res
    
class account_voucher_line(osv.Model):
    _inherit = 'account.voucher.line'
    
    _columns = {
        'line_to_invoice': fields.boolean('Line to Invoice', help='If this field is true indicates'\
            ' that this line coming from an invoice refound')
    }
