# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Julio Serna Hernandez (julio@vauxoo.com)
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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import pooler, tools
from openerp import netsvc
from openerp import release
import time


class ir_attachment_facturae_mx(osv.Model):

    _inherit = 'ir.attachment.facturae.mx'

    def signal_cancel(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = super(ir_attachment_facturae_mx, self).signal_cancel(cr, uid, ids)
        for att in self.browse(cr, uid, ids):
            if res and att.model_source == 'hr.payslip' and att.id_source:
                if self.pool.get(att.model_source).browse(cr, uid, att.id_source).state != 'cancel':
                    res = self.pool.get(att.model_source).cancel_sheet(
                        cr, uid, [att.id_source], context=context)
        return res

class hr_payslip(osv.Model):

    _inherit = 'hr.payslip'
    
    def cancel_sheet(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = super(hr_payslip, self).cancel_sheet(cr, uid, ids, context=context)
        ids = isinstance(ids, (int, long)) and [ids] or ids
        ir_attach_facturae_mx_obj = self.pool.get('ir.attachment.facturae.mx')
        for payslip in self.browse(cr, uid, ids, context=context):
            ir_attach_facturae_mx_ids = ir_attach_facturae_mx_obj.search(
                cr, uid, [('id_source', '=', payslip.id), ('model_source', '=', self._name)], context=context)
            if ir_attach_facturae_mx_ids:
                for attach in ir_attach_facturae_mx_obj.browse(cr, uid, ir_attach_facturae_mx_ids, context=context):
                    if attach.state <> 'cancel':
                        attach = ir_attach_facturae_mx_obj.signal_cancel(cr, uid, [attach.id], context=context)
                        if attach:
                            self.write(cr, uid, ids, {'date_payslip_cancel': time.strftime('%Y-%m-%d %H:%M:%S')})
        return res
