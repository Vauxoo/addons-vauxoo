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
from pytz import timezone
import pytz
from dateutil.relativedelta import relativedelta

import time
import os


class account_payment_term(osv.Model):
    _inherit = "account.payment.term"

    def compute(self, cr, uid, id, value, date_ref=False, context=None):
        if context is None:
            context = {}
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
    #_order = 'invoice_datetime asc'

    def _get_date_invoice_tz(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if context is None:
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
        
    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        if default is None:
            default = {}
        default.update({'invoice_datetime': False, 'date_invoice' : False})
        return super(account_invoice, self).copy(cr, uid, id, default, context)
    
    def _get_time_zone(self, cr, uid, invoice_id, context=None):
        if context is None:
            context = {}
        res_users_obj = self.pool.get('res.users')
        userstz = res_users_obj.browse(cr, uid, [uid])[0].partner_id.tz
        a = 0
        if userstz:
            hours = timezone(userstz)
            fmt = '%Y-%m-%d %H:%M:%S %Z%z'
            now = datetime.datetime.now()
            loc_dt = hours.localize(datetime.datetime(now.year, now.month, now.day,
                                             now.hour, now.minute, now.second))
            timezone_loc = (loc_dt.strftime(fmt))
            diff_timezone_original = timezone_loc[-5:-2]
            timezone_original = int(diff_timezone_original)
            s = str(datetime.datetime.now(pytz.timezone(userstz)))
            s = s[-6:-3]
            timezone_present = int(s)*-1
            a = timezone_original + ((
                timezone_present + timezone_original)*-1)
        return a
    
    def assigned_datetime(self, cr, uid, values, context=None):
        if context is None:
            context = {}
        res = {}
        if values.get('date_invoice', False) and\
                                    not values.get('invoice_datetime', False):
                                    
            user_hour = self._get_time_zone(cr, uid, [], context=context)
            time_invoice = datetime.time(abs(user_hour), 0, 0)

            date_invoice = datetime.datetime.strptime(
                values['date_invoice'], '%Y-%m-%d').date()
                
            dt_invoice = datetime.datetime.combine(
                date_invoice, time_invoice).strftime('%Y-%m-%d %H:%M:%S')

            res['invoice_datetime'] = dt_invoice
            res['date_invoice'] = values['date_invoice']
            
        if values.get('invoice_datetime', False) and not\
            values.get('date_invoice', False):
            date_invoice = fields.datetime.context_timestamp(cr, uid,
                datetime.datetime.strptime(values['invoice_datetime'],
                tools.DEFAULT_SERVER_DATETIME_FORMAT), context=context)
            res['date_invoice'] = date_invoice
            res['invoice_datetime'] = values['invoice_datetime']
        
        if 'invoice_datetime' in values  and 'date_invoice' in values:
            if values['invoice_datetime'] and values['date_invoice']:
                date_invoice = datetime.datetime.strptime(
                    values['invoice_datetime'],
                    '%Y-%m-%d %H:%M:%S').date().strftime('%Y-%m-%d')
                if date_invoice != values['date_invoice']:
                    groups_obj = self.pool.get('res.groups')
                    group_datetime = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'l10n_mx_invoice_datetime', 'group_datetime_invoice_l10n_mx_facturae')
                    group_date = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'l10n_mx_invoice_datetime', 'group_date_invoice_l10n_mx_facturae')
                    if group_datetime and group_date:
                        users_datetime = []
                        users_date = []
                        for user in groups_obj.browse(cr, uid, [group_datetime[1]], context=context)[0].users:
                            users_datetime.append(user.id)
                        for user in groups_obj.browse(cr, uid, [group_date[1]], context=context)[0].users:
                            users_date.append(user.id)
                        if uid in users_datetime:
                            date_invoice = fields.datetime.context_timestamp(cr, uid,
                                datetime.datetime.strptime(values['invoice_datetime'],
                                tools.DEFAULT_SERVER_DATETIME_FORMAT), context=context)
                            res['date_invoice'] = date_invoice
                            res['invoice_datetime'] = values['invoice_datetime']
                        elif uid in users_date:
                            user_hour = self._get_time_zone(cr, uid, [], context=context)
                            time_invoice = datetime.time(abs(user_hour), 0, 0)

                            date_invoice = datetime.datetime.strptime(
                                values['date_invoice'], '%Y-%m-%d').date()
                                
                            dt_invoice = datetime.datetime.combine(
                                date_invoice, time_invoice).strftime('%Y-%m-%d %H:%M:%S')

                            res['invoice_datetime'] = dt_invoice
                            res['date_invoice'] = values['date_invoice']
                        else:
                            raise osv.except_osv(_('Warning!'), _('Invoice dates should be equal'))
                    else:
                        raise osv.except_osv(_('Warning!'), _('Invoice dates should be equal'))
                            
        if  not values.get('invoice_datetime', False) and\
                                        not values.get('date_invoice', False):
            res['date_invoice'] = fields.date.context_today(self,cr,uid,context=context)
            res['invoice_datetime'] = fields.datetime.now()
            
        return res

    def action_move_create(self, cr, uid, ids, context=None):
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.type in ('out_invoice', 'out_refund'):
                vals_date = self.assigned_datetime(cr, uid,
                    {'invoice_datetime': inv.invoice_datetime,
                        'date_invoice': inv.date_invoice},
                        context=context)
                self.write(cr, uid, ids, vals_date, context=context)
        return super(account_invoice,
                        self).action_move_create(cr, uid, ids, context=context)
