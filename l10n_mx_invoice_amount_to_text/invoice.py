# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Launchpad Project Manager for Publication: Nhomar Hernandez - nhomar@openerp.com.ve
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

from osv import osv
from osv import fields
from tools.translate import _
import amount_to_text_es_MX

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def _get_amount_to_text(self, cr, uid, ids, field_names=None, arg=False, context={}):
        if not context:
            context={}
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            amount_to_text = amount_to_text_es_MX.get_amount_to_text(self, invoice.amount_total, 'es_cheque', invoice.currency_id._columns.has_key('code') and invoice.currency_id.code or invoice.currency_id.name)
            res[invoice.id] = amount_to_text
        return res
    
    _columns = {
        'amount_to_text':  fields.function(_get_amount_to_text, method=True, type='char', size=256, string='Amount to Text', store=True),
    }
account_invoice()
