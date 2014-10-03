#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Luis Ernesto García Medina(ernesto_gm@vauxoo.com)
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

from openerp import netsvc
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class account_invoice(osv.Model):
    _name = "account.invoice"
    _inherit = 'account.invoice'
    
    def action_validate_ref_invoice(self, cr, uid, ids, context = None):
        invoice_obj = self.pool.get('account.invoice')
        invoice_duplicate_ids = []
        for invoice in self.browse(cr, uid, ids):
            invoice_ids = invoice_obj.search(cr, uid, [('supplier_invoice_number', '<>', None), 
                        ('company_id' , '=', invoice.company_id.id), ('type', '=', invoice.type)])
            if invoice.supplier_invoice_number:
                for invoice_r in invoice_obj.browse(cr, uid, invoice_ids):
                    if invoice.id != invoice_r.id and invoice.partner_id.id == \
                        invoice_r.partner_id.id and invoice.supplier_invoice_number.upper() == \
                        invoice_r.supplier_invoice_number.upper() and invoice_r.state != 'cancel':
                            invoice_duplicate_ids.append(invoice_r.id)
            if invoice_duplicate_ids:
                raise osv.except_osv(_('Invalid Action!'), _('Error you can not validate the'\
                    ' invoice with supplier invoice number duplicated.'))
        return True

    def invoice_validate(self, cr, uid, ids, context=None):
        self.action_validate_ref_invoice(cr, uid, ids, context = None)
        return super(account_invoice, self).invoice_validate(cr, uid, ids, context=context)
