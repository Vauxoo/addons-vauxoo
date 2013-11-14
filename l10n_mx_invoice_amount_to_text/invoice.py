# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Launchpad Project Manager for Publication: Nhomar Hernandez - nhomar@vauxoo.com
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
from openerp.tools.translate import _
from openerp import pooler, tools
from openerp import netsvc

import amount_to_text_es_MX


class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def _get_amount_to_text(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if context is None:
            context = {}
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            amount_to_text = amount_to_text_es_MX.get_amount_to_text(
                self, invoice.amount_total, 'es_cheque', 'code' in invoice.\
                currency_id._columns and invoice.currency_id.code or invoice.\
                currency_id.name)
            res[invoice.id] = amount_to_text
        return res

    _columns = {
        'amount_to_text':  fields.function(_get_amount_to_text, method=True,
            type='char', size=256, string='Amount to Text', store=True,
            help='Amount of the invoice in letter'),
    }
