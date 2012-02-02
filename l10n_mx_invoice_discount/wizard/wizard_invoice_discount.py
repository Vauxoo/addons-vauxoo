# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    Info (info@vauxoo.com)
############################################################################
#    Coded by: isaac (isaac@vauxoo.com)
#    Coded by: moylop260 (moylop260@vauxoo.com)
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
from osv import fields, osv
import time
#from tools.translate import _
#import pooler


class wizard_invoice_discount(osv.osv_memory):
    _name='wizard.invoice.discount'

    def apply_discount(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoice = invoice_obj.browse(cr, uid, context['active_id'])
        
        if invoice.state == 'draft':
            data = {'line_ids': []}
            for line in invoice.invoice_line:
                discount_dic = {
                    'discount': invoice.partner_id.discount,
                }
                invoice_line_obj.write(cr, uid, line.id, discount_dic)
        else:
            raise osv.except_osv('Warning !', 'El estado de la factura debe ser borrador')
        return {}

wizard_invoice_discount()
