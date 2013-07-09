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

class update_amount_base_tax_wizard(osv.osv_memory):
    _name = 'update.amount.tax.wizard'
    
    def update_tax_secondary(self, cr, uid, ids, context=None):
        acc_tax_obj = self.pool.get('account.tax')
        user_obj = self.pool.get('res.users')
        move_line_obj = self.pool.get('account.move.line')
        acc_tax_category_obj = self.pool.get('account.tax.category')
        company_user_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
        category_iva_ids = acc_tax_category_obj.search(cr, uid, [\
            ('name', 'in', ('IVA', 'IVA-EXENTO', 'IVA-RET'))], context=context)
        tax_ids = acc_tax_obj.search(cr, uid, [('company_id', '=' ,company_user_id), ('type_tax_use', '=', 'purchase'),
            ('tax_category_id', 'in', category_iva_ids)], context=context)
        acc_collected_ids = []
        for tax in acc_tax_obj.browse(cr, uid, tax_ids, context=context):
            acc_collected_ids.append(tax.account_collected_id.id)
        line_id = move_line_obj.search(cr, uid, [('account_id', 'in', acc_collected_ids), ('tax_id_secondary', '=', None)], context=context)
        for line in move_line_obj.browse(cr, uid, line_id, context=context):
            acc_line = line.account_id.id
            tax_this_line = acc_tax_obj.search(cr, uid, [('account_collected_id', '=', acc_line)])
            #~ if len(tax_this_line) == 1:
            if tax_this_line:
                cr.execute("""UPDATE account_move_line
                    SET tax_id_secondary = %s
                    WHERE id = %s""", (tax_this_line[0], line.id))
        return True
    
    def apply(self, cr, uid, ids, context=None):
        self.update_tax_secondary(cr, uid, ids, context=context)
        invoice_obj = self.pool.get('account.invoice')
        move_line_obj = self.pool.get('account.move.line')
        acc_tax_category_obj = self.pool.get('account.tax.category')
        acc_tax_obj = self.pool.get('account.tax')
        user_obj = self.pool.get('res.users')
        company_user_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
        for invoice_id in invoice_obj.search(cr, uid, [('type', '=', 'in_invoice'), '|', ('state', '=', 'open'), ('state', '=', 'paid'), ('company_id', '=',  company_user_id)], context=context):
            invoice = invoice_obj.browse(cr, uid, invoice_id, context=context)
            move_lines = invoice.move_id.line_id or []
            line_ids = [x.id for x in move_lines]
            for tax in invoice.tax_line:
                if tax.name == 'IVA(16%) COMPRAS':
                    move_16 = move_line_obj.search(cr, uid, [('id', 'in', line_ids), ('name', '=', 'IVA(16%) COMPRAS')], context=context)
                    if move_16:
                        move_line_obj.write(cr, uid, move_16[0], {'amount_base' : tax.base_amount}, context=context)
                if tax.name == 'IVA(11%) COMPRAS':
                    move_11 = move_line_obj.search(cr, uid, [('id', 'in', line_ids), ('name', '=', 'IVA(11%) COMPRAS')], context=context)
                    if move_11:
                        move_line_obj.write(cr, uid, move_11[0], {'amount_base' : tax.base_amount}, context=context)
                if tax.name == 'IVA(0%) COMPRAS':
                    move_0 = move_line_obj.search(cr, uid, [('id', 'in', line_ids), ('name', '=', 'IVA(0%) COMPRAS')], context=context)
                    if move_0:
                        move_line_obj.write(cr, uid, move_0[0], {'amount_base' : tax.base_amount}, context=context)
        category_iva_ids = acc_tax_category_obj.search(cr, uid, [\
            ('name', 'in', ('IVA', 'IVA-EXENTO', 'IVA-RET'))], context=context)
        tax_ids = acc_tax_obj.search(cr, uid, [('company_id', '=' ,company_user_id), ('type_tax_use', '=', 'purchase'),
            ('tax_category_id', 'in', category_iva_ids)], context=context)
        lines_without_amount = move_line_obj.search(cr, uid, [('tax_id_secondary', 'in', tax_ids), ('amount_base', '=', False)])
        print 'move_line_obj.browse(cr, uid, lines_without_amount, context=context)', move_line_obj.browse(cr, uid, lines_without_amount, context=context)
        for move in move_line_obj.browse(cr, uid, lines_without_amount, context=context):
            amount_tax = move.tax_id_secondary.amount
            if move.debit != 0:
                amount_base = move.debit
            if move.credit != 0:
                amount_base = move.credit
            if amount_tax != 0:
                cr.execute("""UPDATE account_move_line
                    SET amount_base = %s
                    WHERE id = %s""", (amount_base/amount_tax, move.id))
        return True
