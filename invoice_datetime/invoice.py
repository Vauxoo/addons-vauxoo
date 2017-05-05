# coding: utf-8
# ##########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
# ###########################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Launchpad Project Manager for Publication:
#             * Nhomar Hernandez - nhomar@vauxoo.com
# ###########################################################################
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
# #############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import tools, api
import datetime
from datetime import timedelta
from pytz import timezone
import pytz
import time


class AccountPaymentTerm(osv.Model):
    _inherit = "account.payment.term"

    # pylint: disable=W0622
    def compute(self, cr, uid, id, value,
                date_ref=False, context=None):
        if context is None:
            context = {}
        if date_ref:
            try:
                date_ref = time.strftime('%Y-%m-%d', time.strptime(
                    date_ref, '%Y-%m-%d %H:%M:%S'))
            except BaseException:
                pass
        return super(AccountPaymentTerm, self).compute(
            cr, uid, id, value, date_ref, context=context)


class AccountInvoice(osv.Model):
    _inherit = 'account.invoice'
    # _order = 'invoice_datetime asc'

    def _get_field_params(self, cr, uid, ids, name, unknow_none, context=None):
        if context is None:
            context = {}
        account_setting_obj = self.pool.get("account.config.settings")
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = {}
        key_by_company_id = "acc_invoice.date_invoice_type_" + \
                            str(account_setting_obj._default_company(cr, uid))
        res[ids[0]] = self.pool.get("ir.config_parameter").get_param(
            cr, uid, key_by_company_id, default='date', context=context)
        return res

    _columns = {
        # Extract date_invoice from original, but add datetime
        # 'date_invoice': fields.datetime('Date Invoiced', states={'open':[
        # ('readonly',True)],'close':[('readonly',True)]},
        # help="Keep empty to use the current date"),
        'invoice_datetime': fields.datetime(
            'Date time of invoice',
            states={
                'open': [('readonly', True)],
                'close': [('readonly', True)]},
            help="Keep empty to use the current date"),
        'date_invoice_tz': fields.datetime(
            string='Date Invoiced with TZ',
            help='Date of Invoice with Time Zone'),
        'date_type': fields.function(_get_field_params, storage=False,
                                     type='char', string="Date type")
    }

    def _get_datetime_with_user_tz(self, cr, uid, datetime_invoice=False,
                                   context=None):
        datetime_inv_tz = False
        if datetime_invoice:
            time_tz = self.pool.get("res.users").read(
                cr, uid, uid, ["tz_offset"], context=context).get("tz_offset")
            hours_tz = int(time_tz[:-2])
            minut_tz = int(time_tz[-2:])
            if time_tz[0] == '-':
                minut_tz = minut_tz * -1
            datetime_inv_tz = (
                datetime_invoice + timedelta(
                    hours=hours_tz,
                    minutes=minut_tz)).strftime('%Y-%m-%d %H:%M:%S')
        return datetime_inv_tz

    def create(self, cr, uid, vals, context=None):
        account_setting_obj = self.pool.get("account.config.settings")
        key_by_company_id = "acc_invoice.date_invoice_type_" + \
                            str(account_setting_obj._default_company(cr, uid))
        type_date = self.pool.get("ir.config_parameter").get_param(
            cr, uid, key_by_company_id, default='date', context=context)
        if type_date == "datetime":
            if vals.get("type", False) in ("out_invoice", "out_refund"):
                if vals.get('date_invoice', False):
                    inv_date = vals.pop("date_invoice")
                    invoice_datetime = inv_date + " " + \
                        datetime.datetime.strptime(
                            fields.datetime.now(),
                            "%Y-%m-%d %H:%M:%S").strftime('%H:%M:%S')
                    vals.update({'invoice_datetime': invoice_datetime})
        if 'invoice_datetime' in vals.keys():
            datetime_inv = vals.get("invoice_datetime") and \
                datetime.datetime.strptime(
                    vals.get("invoice_datetime"), "%Y-%m-%d %H:%M:%S") or False
            if datetime_inv:
                vals.update(
                    {'date_invoice_tz': self._get_datetime_with_user_tz(
                        cr, uid, datetime_inv)})
        return super(AccountInvoice, self).create(
            cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        for invoice in self.browse(cr, uid, ids, context=context):
            datetime_inv = invoice.invoice_datetime and \
                datetime.datetime.strptime(invoice.invoice_datetime,
                                           "%Y-%m-%d %H:%M:%S") or False
            if datetime_inv and not invoice.date_invoice_tz:
                vals.update(
                    {'date_invoice_tz': self._get_datetime_with_user_tz(
                        cr, uid, datetime_inv)})
        return super(AccountInvoice, self).write(
            cr, uid, ids, vals, context=context)

    def _get_default_type(self, cr, uid, ids):
        account_setting_obj = self.pool.get("account.config.settings")
        key_by_company_id = "acc_invoice.date_invoice_type_" + \
            str(account_setting_obj._default_company(cr, uid))
        type_show_date = self.pool.get("ir.config_parameter").get_param(
            cr, uid, key_by_company_id, default='date')
        return type_show_date

    _defaults = {
        # 'date_invoice': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        "date_type": _get_default_type
    }

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default.update({
            'invoice_datetime': False,
            'date_invoice': False,
            'date_invoice_tz': False})
        return super(AccountInvoice, self).copy(default)

    def _get_time_zone(self, cr, uid, invoice_id, context=None):
        if context is None:
            context = {}
        res_users_obj = self.pool.get('res.users')
        userstz = res_users_obj.browse(cr, uid, [uid])[0].partner_id.tz
        result = 0
        if userstz:
            hours = timezone(userstz)
            fmt = '%Y-%m-%d %H:%M:%S %Z%z'
            now = datetime.datetime.now()
            loc_dt = hours.localize(datetime.datetime(now.year, now.month,
                                                      now.day, now.hour,
                                                      now.minute, now.second))
            timezone_loc = (loc_dt.strftime(fmt))
            diff_timezone_original = timezone_loc[-5:-2]
            timezone_original = int(diff_timezone_original)
            str_datetime = str(datetime.datetime.now(pytz.timezone(userstz)))
            str_datetime = str_datetime[-6:-3]
            timezone_present = int(str_datetime) * -1
            result = timezone_original + ((
                timezone_present + timezone_original) * -1)
        return result

    def assigned_datetime(self, cr, uid, ids, values, context=None):
        if context is None:
            context = {}
        res = {}
        if values.get('date_invoice', False) and\
                not values.get('invoice_datetime', False):
            user_hour = self._get_time_zone(cr, uid, [], context=context)
            time_invoice = datetime.datetime.utcnow().time()

            date_invoice = datetime.datetime.strptime(
                values['date_invoice'], '%Y-%m-%d').date()

            dt_invoice = datetime.datetime.combine(
                date_invoice, time_invoice).strftime('%Y-%m-%d %H:%M:%S')

            res['invoice_datetime'] = dt_invoice
            res['date_invoice'] = values['date_invoice']

        if values.get('invoice_datetime', False) and not\
                values.get('date_invoice', False):
            date_invoice = fields.datetime.context_timestamp(
                cr, uid, datetime.datetime.strptime(
                    values['invoice_datetime'],
                    tools.DEFAULT_SERVER_DATETIME_FORMAT), context=context)
            res['date_invoice'] = date_invoice
            res['invoice_datetime'] = values['invoice_datetime']

        if 'invoice_datetime' in values and 'date_invoice' in values:
            if values['invoice_datetime'] and values['date_invoice']:
                date_invoice = datetime.datetime.strptime(
                    values['invoice_datetime'],
                    '%Y-%m-%d %H:%M:%S').date().strftime('%Y-%m-%d')
                if date_invoice != values['date_invoice']:
                    if self.browse(cr, uid, ids)[0].date_type == 'datetime':
                        date_invoice = fields.datetime.context_timestamp(
                            cr, uid, datetime.datetime.strptime(
                                values['invoice_datetime'],
                                tools.DEFAULT_SERVER_DATETIME_FORMAT),
                            context=context)
                        res['date_invoice'] = date_invoice
                        res['invoice_datetime'] = values['invoice_datetime']
                    elif self.browse(cr, uid, ids)[0].date_type == 'date':
                        user_hour = self._get_time_zone(
                            cr, uid, [], context=context)
                        time_invoice = datetime.time(abs(user_hour), 0, 0)

                        date_invoice = datetime.datetime.strptime(
                            values['date_invoice'], '%Y-%m-%d').date()

                        dt_invoice = datetime.datetime.combine(
                            date_invoice,
                            time_invoice).strftime('%Y-%m-%d %H:%M:%S')

                        res['invoice_datetime'] = dt_invoice
                        res['date_invoice'] = values['date_invoice']
                    else:
                        raise osv.except_osv(
                            _('Warning!'),
                            _('Invoice dates should be equal'))
                    # ~ else:
                    # ~ raise osv.except_osv(_('Warning!'),
                    # _('Invoice dates should be equal'))

        if not values.get('invoice_datetime', False) and\
                not values.get('date_invoice', False):
            res['date_invoice'] = fields.date.context_today(
                self, cr, uid, context=context)
            res['invoice_datetime'] = fields.datetime.now()

        return res

    def action_move_create(self, cr, uid, ids, context=None):
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.type in ('out_invoice', 'out_refund'):
                vals_date = self.assigned_datetime(
                    cr, uid, ids, {'invoice_datetime': inv.invoice_datetime,
                                   'date_invoice': inv.date_invoice},
                    context=context)
                self.write(cr, uid, ids, vals_date, context=context)
        return super(AccountInvoice,
                     self).action_move_create(cr, uid, ids, context=context)
