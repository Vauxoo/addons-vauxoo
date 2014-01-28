#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: vauxoo consultores (info@vauxoo.com)
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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import pooler, tools

class ir_attachment_facturae_mx(osv.Model):

    _inherit = 'ir.attachment.facturae.mx'

    _columns = {
        'journal_id': fields.many2one('account.journal','Journal'),
        'payroll_id': fields.many2one('hr.payslip', 'Payslip'),
    }

class hr_payslip_product_line(osv.Model):
    
    _name = 'hr.payslip.product.line'

    _columns = {
        'payslip_id': fields.many2one('hr.payslip'),
        'product_id': fields.many2one('product.product', 'Product'),
        'amount': fields.float('Amount')
    }

class hr_payslip(osv.Model):

    _inherit = 'hr.payslip'

    _columns = {
        'journal_id': fields.many2one('account.journal','Journal'),
        'date_payslip': fields.date('Payslip Date'),
        'line_payslip_product_ids': fields.one2many('hr.payslip.product.line', 'payslip_id', 'Generic Product'),
        'pay_method_id': fields.many2one('pay.method', 'Payment Method',
            readonly=True, states={'draft': [('readonly', False)]}),
    }

    def hr_verify_sheet(self, cr, uid, ids, context=None):
        super(hr_payslip, self).hr_verify_sheet(cr, uid, ids)
        result = self.create_ir_attachment_payroll(cr, uid, ids, context)
        return result

    def create_ir_attachment_payroll(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        attach = ''
        ir_attach_obj = self.pool.get('ir.attachment.facturae.mx')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        attach_ids = []
        for payroll in self.browse(cr, uid, ids, context=context):
            type = payroll.journal_id and payroll.journal_id.sequence_id and payroll.journal_id.sequence_id.approval_ids[0] and payroll.journal_id.sequence_id.approval_ids[0].type
            attach_ids.append( ir_attach_obj.create(cr, uid, {
              'name': payroll.number or '/', 'type': type,
              'journal_id': payroll.journal_id and payroll.journal_id.id or False,
              'payroll_id': payroll and payroll.id or False},
              context=None)#Context, because use a variable type of our code but we dont need it.
            )
        if attach_ids:
            result = mod_obj.get_object_reference(cr, uid, 'l10n_mx_ir_attachment_facturae',
                                                            'action_ir_attachment_facturae_mx')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
            #choose the view_mode accordingly
            result['domain'] = "[('id','in',["+','.join(map(str, attach_ids))+"])]"
            result['res_id'] = attach_ids and attach_ids[0] or False
            res = mod_obj.get_object_reference(cr, uid, 'l10n_mx_ir_attachment_facturae', 
                                                            'view_ir_attachment_facturae_mx_form')
            result['views'] = [(res and res[1] or False, 'form')]
            return result
        return True
