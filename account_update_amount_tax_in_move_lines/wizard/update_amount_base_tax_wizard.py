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
    
    def apply(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        move_line_obj = self.pool.get('account.move.line')
        user_obj = self.pool.get('res.users')
        company_user_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
        for invoice_id in invoice_obj.search(cr, uid, [('type', '=', 'in_invoice'), ('state', '!=', 'draf'), ('company_id', '=',  company_user_id)], context=context):
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
        return True
