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
from openerp.osv import fields, osv


class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'expense_id': fields.many2one('hr.expense.expense', 'Expense',
                                      help='Expense Document Name'),
    }

    def create_expense_from_invoice(self, cr, uid, ids, context=None):
        """ Create an hr expense object from a invoice object """
        #~ TODO: Necesito verificar si el partner es un empleado????
        context = context or {}
        exp_obj = self.pool.get('hr.expense.expense')
        for inv_brw in self.browse(cr, uid, ids, context=context):
            vals = {'name': 'Expenses for employee ' + inv_brw.partner_id.name}
            exp_id = exp_obj.create(cr, uid, vals, context=context)
            self.create_expense_lines(cr, uid, inv_brw.id, exp_id,
                                      context=context)
            self.write(cr, uid, inv_brw.id, {'expense_id': exp_id},
                       context=context)
        return True

    def create_expense_lines(self, cr, uid, ids, exp_id, context=None):
        """ Create hr expense lines from a invoices lines and associated to a
        pre created hr expense object.
        @param exp_id: expense document ide
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        exp_obj = self.pool.get('hr.expense.expense')
        expl_obj = self.pool.get('hr.expense.line')
        for inv_brw in self.browse(cr, uid, ids, context=context):
            data = []
            for line_brw in inv_brw.invoice_line:
                vals = dict()
                vals['invoice_id'] = inv_brw.id
                vals['product_id'] = line_brw.product_id and \
                    line_brw.product_id.id or False
                vals['name'] = line_brw.name or 'No description given'
                vals['uom_id'] = line_brw.uos_id and line_brw.uos_id.id or \
                    expl_obj.default_get(
                        cr, uid, ['uom_id'], context=context)['uom_id']
                vals['unit_amount'] = line_brw.price_unit
                vals['unit_quantity'] = line_brw.quantity
                data.append((0, 0, vals))
            exp_obj.write(cr, uid, exp_id, {'line_ids': data}, context=context)
        return True


class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
    _columns = {
        'expense_id': fields.related('invoice_id', 'expense_id',
                                     relation='hr.expense.expense',
                                     type="many2one",
                                     string='Expense',
                                     help='Expense Document Name',
                                     store=True),
    }
    
