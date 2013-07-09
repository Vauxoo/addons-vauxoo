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

class hr_expense_line(osv.osv):
    _inherit = "hr.expense.line"

    _columns = {
        'invoice_id': fields.many2one('account.invoice', 'Invoice',
                                      ondelete='cascade'),
        #~ NOTE: this field is really a one2one
    }

    def fields_get(self, cr, user, allfields=None, context=None,
                   write_access=True):
        """ Overwrite the method to add the domin of type of invoice into the
        many2one hr expense line that it shows in ht expense form.
        """
        context = context or {}
        res = super(hr_expense_line,self).fields_get(cr, user, allfields,
                    context, write_access)
        res['invoice_id']['domain'].append(('type','=','in_invoice'))
        return res

class hr_expense_expense(osv.osv):
    _inherit = "hr.expense.expense"

    _columns = {
        'invoice_ids': fields.one2many(
            'account.invoice', 'expense_id', 'Invoices',
            help='Lines being recorded in the book'),
    }

    def action_receipt_create(self, cr, uid, ids, context=None):
        """ Overwrite the action_receipt_create function to add the validate
        invoice process """
        context = context or {}
        error_msj = str()
        for exp_brw in self.browse(cr, uid, ids, context=context):
            for line_exp_brw in exp_brw.line_ids:
                if line_exp_brw.invoice_id:
                    if line_exp_brw.invoice_id.state == 'open':
                        # create accounting entries related to an expense
                        super(hr_expense_expense, self).action_receipt_create(cr, uid, ids,
                                                                              context=context)
                    else:
                        error_msj = error_msj + \
                            '- [Expense] ' + exp_brw.name + \
                            ' [Expense Line] ' + line_exp_brw.name +  \
                            ' [Invoice] ' + (line_exp_brw.invoice_id.number or line_exp_brw.invoice_id.partner_id.name) + '\n'
        if error_msj:
            raise osv.except_osv(
                'Invalid Procedure!',
                "You can not generate the Accounting Entries for this Expense."
                " There are some invoices associated to the expenses lines"
                " that are not in open state. Please paid the invoices.\n"
                + error_msj)

        return True

    #~ TODO: Doing
    def concile_viatical_payment(self, cr, uid, ids, context=None):
        """ It concile a new journal entry that englobs the expense accounting
        entry and the invoices accounting entries.
        """
        context = context or {}
        am_obj = self.pool.get('account.move')
        ai_obj = self.pool.get('account.invoice')
        for exp_brw in self.browse(cr, uid, ids, context=context):
            vals = {}
            #~ posted el asiento de lra factura? -> validar la facutra. colocarla en estado open.
            #~ inv_move_id = ... agregar campo a hr.expense? como es esa relacion de muchos?? 
            #~ for inv_brw in exp_brw.invoice_ids:
                #~ inv_move_id = 

            #~ generar asiento del expense. esto es dando el click al boton de
            #~ generate accounintg para dejar la exp en estado done?
            #~ ....
            exp_move_id = exp_brw.account_move_id.id

        #~ create new account move, that containg the data of the hr_expsense acccount move recently created, and the info of the invoice paid.
            #~ name: no estoy segura si necesito colocarlo o si se genera solo?
            #~ state : draft
            #~ ref
            #~ journal_id: un nuevo journal_id
            #~ lines: extraigo la info del acc.move del expense, y la info del acc.move de la factura
                #~ para ello debo de buscar dentro de las acc.move.lines el que tenga credit
            #~ vals['ref'] = 'Pago de Viaticos'
            #~ am_obj.create(cr, uid, vals, context=context)
            #~ self.create_account_move_line(cr, uid, ids, context=context)

        return True

    #~ TODO: Doing
    def create_account_move_line(self, cr, uid, ids, context=None):
        context = context or {}
        am_obj = self.pool.get('account.move')
        aml_obj = self.pool.get('account.move.line')

        for exp_brw in self.browse(cr, uid, ids, context=context):

            vals1['name'] = 'Pago de Viáticos'
            vals1['partner_id'] = exp_brw.employee_id
            #~ vals1['account_id'] = Payable..
            #~ vals1['debit'] = 

        return True

    def refresh_expense_lines(self, cr, uid, ids, context=None):
        """ """
        context = context or {}
        ai_obj = self.pool.get('account.invoice')
        expl_obj = self.pool.get('hr.expense.line')
        for exp_brw in self.browse(cr, uid, ids, context=context):
            expl_ids = [expl_brw.id for expl_brw in exp_brw.line_ids]
            expl_obj.unlink(cr, uid, expl_ids, context=context)
            inv_brws = exp_brw.invoice_ids
            inv_ids = [inv_brw.id for inv_brw in inv_brws]
            ai_obj.create_expense_lines(cr, uid, inv_ids, ids[0], context=context)
        return True
