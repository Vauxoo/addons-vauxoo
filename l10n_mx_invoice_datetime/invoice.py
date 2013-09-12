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
import datetime
import pytz

import time
import os


class account_payment_term(osv.Model):
    _inherit = "account.payment.term"

    def compute(self, cr, uid, id, value, date_ref=False, context={}):
        if date_ref:
            try:
                date_ref = time.strftime('%Y-%m-%d', time.strptime(
                    date_ref, '%Y-%m-%d %H:%M:%S'))
            except:
                pass
        return super(account_payment_term, self).compute(cr, uid, id, value,
            date_ref, context=context)


class account_invoice(osv.Model):
    _inherit = 'account.invoice'
    _order = 'invoice_datetime asc'

    def _get_date_invoice_tz(self, cr, uid, ids, field_names=None, arg=False,
        context={}):
        if not context:
            context = {}
        res = {}
        if release.version >= '6':
            dt_format = tools.DEFAULT_SERVER_DATETIME_FORMAT
            tz = context.get('tz_invoice_mx', 'America/Mexico_City')
            for invoice in self.browse(cr, uid, ids, context=context):
                res[invoice.id] = invoice.invoice_datetime and tools.\
                    server_to_local_timestamp(invoice.invoice_datetime,
                    tools.DEFAULT_SERVER_DATETIME_FORMAT,
                    tools.DEFAULT_SERVER_DATETIME_FORMAT, context.get(
                    'tz_invoice_mx', 'America/Mexico_City')) or False
        elif release.version < '6':
            # TODO: tz change for openerp5
            for invoice in self.browse(cr, uid, ids, context=context):
                res[invoice.id] = invoice.date_invoice
        return res

    _columns = {
        # Extract date_invoice from original, but add datetime
        #'date_invoice': fields.datetime('Date Invoiced', states={'open':[
        #('readonly',True)],'close':[('readonly',True)]},
        #help="Keep empty to use the current date"),
        'invoice_datetime': fields.datetime('Date Electronic Invoiced ',
            states={'open': [('readonly', True)], 'close': [('readonly', True)]},
            help="Keep empty to use the current date"),
        'date_invoice_tz':  fields.function(_get_date_invoice_tz, method=True,
            type='datetime', string='Date Invoiced with TZ', store=True,
            help='Date of Invoice with Time Zone'),
    }

    _defaults = {
        #'date_invoice': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    def create(self, cr, uid, vals, context=None):
        res = self.assigned_datetime(cr, uid, vals, context=context)
        if res:
            vals.update(res)
        return super(account_invoice, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        res = self.assigned_datetime(cr, uid, vals, context=context)
        if res:
            vals.update(res)
        return super(account_invoice, self).write(cr, uid, ids, vals,
                                                        context=context)

    def assigned_datetime(self, cr, uid, values, context=None):
        if context is None:
            context = {}
        res = {}
        if 'date_invoice' in values:
            if values['date_invoice'] and not\
                values.get('invoice_datetime', False):
                date_ts = tools.server_to_local_timestamp(values[
                    'date_invoice'], tools.DEFAULT_SERVER_DATETIME_FORMAT,
                    tools.DEFAULT_SERVER_DATETIME_FORMAT, context.get(
                    'tz_invoice_mx', 'America/Mexico_City'))
                now = datetime.datetime.now()
                time_invoice = datetime.time(now.hour, now.minute, now.second)
                date_invoice = datetime.datetime.strptime(
                    date_ts, '%Y-%m-%d').date()
                dt_invoice = datetime.datetime.combine(
                    date_invoice, time_invoice).strftime('%Y-%m-%d %H:%M:%S')
                res['invoice_datetime'] = dt_invoice
                date_invoice = datetime.datetime.strptime(
                    dt_invoice, '%Y-%m-%d %H:%M:%S').date().strftime('%Y-%m-%d')
                res['date_invoice'] = date_invoice
                return res
            
        if 'invoice_datetime' in values:
            if values['invoice_datetime'] and not\
                values.get('date_invoice', False):
                date_ts = tools.server_to_local_timestamp(values[
                    'invoice_datetime'], tools.DEFAULT_SERVER_DATETIME_FORMAT,
                    tools.DEFAULT_SERVER_DATETIME_FORMAT, context.get(
                    'tz_invoice_mx', 'America/Mexico_City'))
                date_invoice = datetime.datetime.strptime(
                    date_ts, '%Y-%m-%d %H:%M:%S').date().strftime('%Y-%m-%d')
                res['date_invoice'] = date_invoice
                res['invoice_datetime'] = date_ts
                return res
        
        if 'invoice_datetime' in values  and 'date_invoice' in values:
            if values['invoice_datetime'] and values['date_invoice']:
                date_invoice = datetime.datetime.strptime(
                    values['invoice_datetime'],
                    '%Y-%m-%d %H:%M:%S').date().strftime('%Y-%m-%d')
                if date_invoice != values['date_invoice']:
                    raise osv.except_osv(_('Warning!'), _('Date in invoice diferent'))
        return res

    def action_move_create(self, cr, uid, ids, *args):
        for inv in self.browse(cr, uid, ids):
            values = {'date_invoice': inv.date_invoice,
                        'invoice_datetime': inv.invoice_datetime}
            date_value = self.assigned_datetime(cr, uid, values)
            if inv.move_id:
                continue
            if inv.date_invoice and inv.invoice_datetime:
                return super(account_invoice, self).action_move_create(cr,
                                    uid, ids, *args)
            t1 = time.strftime('%Y-%m-%d')
            t2 = time.strftime('%Y-%m-%d %H:%M:%S')
            self.write(cr, uid, [inv.id], {
                       'date_invoice': date_value.get('date_invoice', t1),
                       'invoice_datetime': date_value.get('invoice_datetime', t2)})
        return super(account_invoice, self).action_move_create(cr, uid, ids, *args)

# class account_invoice_refund(osv.TransientModel):
 #   _inherit = 'account.invoice.refund'
  #  _columns = {
   #     'date': fields.datetime('Operation date', help='This date will be used as the invoice date for Refund Invoice and Period will be chosen accordingly!'),
   # }
    # _defaults = {
     #   'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
   # }
