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

from openerp.osv import osv, fields

class account_voucher(osv.Model):
    _inherit = 'account.voucher'
    
    def _get_double_validation_ok(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.type == 'payment' and voucher.journal_id.\
                voucher_double_validation_ok:
                res[voucher.id] = True
            else:
                res[voucher.id] = False
        return res
    
    _columns = {
        'double_validation_ok' : fields.function(_get_double_validation_ok,
            type='boolean', string='Double Validation OK', store=True),
        'tax_paid' : fields.boolean('Amount Tax Paid', help='This field'\
            'show if the tax of this voucher already was paid', readonly=True)
        }
        
    def validate_paid_tax(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            voucher.write({'tax_paid': True})
        return True
    
    def cancel_voucher(self, cr, uid, ids, context=None):
        for voucher in self.browse(cr, uid, ids, context=context):
            voucher.write({'tax_paid': False})
        return super(account_voucher, self).cancel_voucher(cr, uid, ids,
            context=context)

    def proforma_voucher(self, cr, uid, ids, context=None):
        for voucher in self.browse(cr, uid, ids, context=context):
            if not voucher.double_validation_ok:
                voucher.write({'tax_paid': True})
        return super(account_voucher, self).proforma_voucher(cr, uid, ids,
            context=context)
