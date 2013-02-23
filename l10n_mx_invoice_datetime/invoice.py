# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
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
from openerp import release

import time
import os

class account_payment_term(osv.osv):
    _inherit = "account.payment.term"
    
    def compute(self, cr, uid, id, value, date_ref=False, context={}):
        if date_ref:
            try:
                date_ref = time.strftime('%Y-%m-%d', time.strptime(date_ref, '%Y-%m-%d %H:%M:%S'))
            except:
                pass
        return super(account_payment_term, self).compute(cr, uid, id, value, date_ref, context=context)
account_payment_term()

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _order = 'date_invoice asc'
    
    def _get_date_invoice_tz(self, cr, uid, ids, field_names=None, arg=False, context={}):
        if not context:
            context = {}
        res = {}
        if release.version >= '6':
            dt_format = tools.DEFAULT_SERVER_DATETIME_FORMAT
            tz = context.get('tz_invoice_mx', 'America/Mexico_City')
            for invoice in self.browse(cr, uid, ids, context=context):
                res[invoice.id] = invoice.date_invoice and tools.server_to_local_timestamp(invoice.date_invoice, dt_format, dt_format, tz) or False
        elif release.version < '6':
            #TODO: tz change for openerp5
            for invoice in self.browse(cr, uid, ids, context=context):
                res[invoice.id] = invoice.date_invoice
        return res
    
    _columns = {
        ##Extract date_invoice from original, but add datetime
        'date_invoice': fields.datetime('Date Invoiced', states={'open':[('readonly',True)],'close':[('readonly',True)]}, help="Keep empty to use the current date"),
        'date_invoice_tz':  fields.function(_get_date_invoice_tz, method=True, type='datetime', string='Date Invoiced with TZ', store=True),
    }
    
    _defaults = {
        #'date_invoice': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    def action_move_create(self, cr, uid, ids, *args):
        for inv in self.browse(cr, uid, ids):
            if inv.move_id:
                continue
            if not inv.date_invoice:
                self.write(cr, uid, [inv.id], {'date_invoice': time.strftime('%Y-%m-%d %H:%M:%S')})
        return super(account_invoice, self).action_move_create(cr, uid, ids, *args)
account_invoice()

class account_invoice_refund(osv.osv_memory):
    _inherit = 'account.invoice.refund'
    _columns = {
        'date': fields.datetime('Operation date', help='This date will be used as the invoice date for Refund Invoice and Period will be chosen accordingly!'),     
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
account_invoice_refund()
