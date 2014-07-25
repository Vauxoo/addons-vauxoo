# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
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
import openerp.addons.decimal_precision as dp

class hr_payslip(osv.osv):
    _inherit = 'hr.payslip'
    
    def _amount_residual(self, cr, uid, ids, name, args, context=None):
        """Function of the field residua. It computes the residual amount (balance) for each payslip"""
        if context is None:
            context = {}
        ctx = context.copy()
        result = {}
        for payslip in self.browse(cr, uid, ids, context=context):
            nb_inv_in_partial_rec = max_invoice_id = 0
            result[payslip.id] = 0.0
            if payslip.move_id:
                for aml in payslip.move_id.line_id:
                    if aml.account_id.type in ('receivable','payable'):
                        result[payslip.id] += aml.amount_residual_currency
            #prevent the residual amount on the payslip to be less than 0
            result[payslip.id] = max(result[payslip.id], 0.0)            
        return result
    
    def _get_payslip_from_line(self, cr, uid, ids, context=None):
        move = {}
        for line in self.pool.get('account.move.line').browse(cr, uid, ids, context=context):
            if line.reconcile_partial_id:
                for line2 in line.reconcile_partial_id.line_partial_ids:
                    move[line2.move_id.id] = True
            if line.reconcile_id:
                for line2 in line.reconcile_id.line_id:
                    move[line2.move_id.id] = True
        payslip_ids = []
        if move:
            payslip_ids = self.pool.get('hr.payslip').search(cr, uid, [('move_id', 'in', move.keys())], context=context)
        return payslip_ids

    def _get_payslip_from_reconcile(self, cr, uid, ids, context=None):
        move = {}
        for r in self.pool.get('account.move.reconcile').browse(cr, uid, ids, context=context):
            for line in r.line_partial_ids:
                move[line.move_id.id] = True
            for line in r.line_id:
                move[line.move_id.id] = True

        payslip_ids = []
        if move:
            payslip_ids = self.pool.get('hr.payslip').search(cr, uid, [('move_id', 'in', move.keys())], context=context)
        return payslip_ids
        
    _columns = {
        'residual': fields.function(_amount_residual, digits_compute=dp.get_precision('Account'), string='Balance',
            store={
                'hr.payslip': (lambda self, cr, uid, ids, c={}: ids, [], 50),
                'account.move.line': (_get_payslip_from_line, None, 50),
                'account.move.reconcile': (_get_payslip_from_reconcile, None, 50),
            },),
        }
