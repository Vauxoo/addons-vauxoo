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

from openerp import fields, models, api
from openerp.exceptions import UserError
from openerp.tools.translate import _
from openerp import tools, api
import datetime
from datetime import timedelta
from pytz import timezone
import pytz


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    # _order = 'invoice_datetime asc'

    @api.multi
    def _get_field_params(self):
        for record in self:
            key_by_company_id = "acc_invoice.date_invoice_type_" + \
                                str(self.company_id.id)
            record.date_type = self.env["ir.config_parameter"].get_param(
                key_by_company_id, default='date')

    @api.multi
    def _get_default_type(self):
        account_setting_obj = self.env["account.config.settings"]
        key_by_company_id = "acc_invoice.date_invoice_type_" + \
            str(account_setting_obj._default_company())
        type_show_date = self.env["ir.config_parameter"].get_param(
            key_by_company_id, default='date')
        return type_show_date

    # Extract date_invoice from original, but add datetime
    # 'date_invoice': fields.datetime('Date Invoiced', states={'open':[
    # ('readonly',True)],'close':[('readonly',True)]},
    # help="Keep empty to use the current date"),
    invoice_datetime = fields.Datetime(
        string='Date time of invoice',
        states={
            'open': [('readonly', True)],
            'close': [('readonly', True)]},
        help="Keep empty to use the current date")
    date_invoice_tz = fields.Datetime(
        string='Date Invoiced with TZ',
        help='Date of Invoice with Time Zone')
    date_type = fields.Char(
        compute=_get_field_params,
        string="Date type",
        default=_get_default_type)

    @api.multi
    def _get_datetime_with_user_tz(self, datetime_invoice=False):
        datetime_inv_tz = False
        if datetime_invoice:
            time_tz = self.env.user.tz_offset
            hours_tz = int(time_tz[:-2])
            minut_tz = int(time_tz[-2:])
            if time_tz[0] == '-':
                minut_tz = minut_tz * -1
            datetime_inv_tz = (
                datetime_invoice + timedelta(
                    hours=hours_tz,
                    minutes=minut_tz)).strftime('%Y-%m-%d %H:%M:%S')
        return datetime_inv_tz

    @api.model
    def create(self, vals):
        if 'invoice_datetime' in vals.keys():
            datetime_inv = vals.get("invoice_datetime") and \
                datetime.datetime.strptime(
                    vals.get("invoice_datetime"), "%Y-%m-%d %H:%M:%S") or False
            if datetime_inv:
                vals.update(
                    {'date_invoice_tz': self._get_datetime_with_user_tz(
                        datetime_inv)})
        return super(AccountInvoice, self).create(vals)

    @api.multi
    def write(self, vals):
        for invoice in self:
            datetime_inv = invoice.invoice_datetime and \
                datetime.datetime.strptime(invoice.invoice_datetime,
                                           "%Y-%m-%d %H:%M:%S") or False
            if datetime_inv and not invoice.date_invoice_tz:
                vals.update(
                    {'date_invoice_tz': self._get_datetime_with_user_tz(
                        datetime_inv)})
        return super(AccountInvoice, self).write(vals)

    # _defaults = {
    #     # 'date_invoice': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    #     "date_type": _get_default_type
    # }

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        default.update({
            'invoice_datetime': False,
            'date_invoice': False,
            'date_invoice_tz': False})
        return super(AccountInvoice, self).copy(default)

    @api.multi
    def _get_time_zone(self, invoice_id):
        userstz = self.env.user.partner_id.tz
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

    @api.multi
    def assigned_datetime(self, values):
        res = {}
        if values.get('date_invoice', False) and\
                not values.get('invoice_datetime', False):
            user_hour = self._get_time_zone([])
            time_invoice = datetime.datetime.utcnow().time()

            date_invoice = datetime.datetime.strptime(
                values['date_invoice'], '%Y-%m-%d').date()

            dt_invoice = datetime.datetime.combine(
                date_invoice, time_invoice).strftime('%Y-%m-%d %H:%M:%S')

            res['invoice_datetime'] = dt_invoice
            res['date_invoice'] = values['date_invoice']

        if values.get('invoice_datetime', False) and not\
                values.get('date_invoice', False):
            date_invoice = fields.Datetime.context_timestamp(
                datetime.datetime.strptime(
                    values['invoice_datetime'],
                    tools.DEFAULT_SERVER_DATETIME_FORMAT))
            res['date_invoice'] = date_invoice
            res['invoice_datetime'] = values['invoice_datetime']

        if 'invoice_datetime' in values and 'date_invoice' in values:
            if values['invoice_datetime'] and values['date_invoice']:
                date_invoice = datetime.datetime.strptime(
                    values['invoice_datetime'],
                    '%Y-%m-%d %H:%M:%S').date().strftime('%Y-%m-%d')
                if date_invoice != values['date_invoice']:
                    if self.date_type == 'datetime':
                        date_invoice = fields.Datetime.context_timestamp(
                            datetime.datetime.strptime(
                                values['invoice_datetime'],
                                tools.DEFAULT_SERVER_DATETIME_FORMAT))
                        res['date_invoice'] = date_invoice
                        res['invoice_datetime'] = values['invoice_datetime']
                    elif self.date_type == 'date':
                        user_hour = self._get_time_zone([])
                        time_invoice = datetime.time(abs(user_hour), 0, 0)

                        date_invoice = datetime.datetime.strptime(
                            values['date_invoice'], '%Y-%m-%d').date()

                        dt_invoice = datetime.datetime.combine(
                            date_invoice,
                            time_invoice).strftime('%Y-%m-%d %H:%M:%S')

                        res['invoice_datetime'] = dt_invoice
                        res['date_invoice'] = values['date_invoice']
                    else:
                        raise UserError(
                            _('Warning!'),
                            _('Invoice dates should be equal'))
                    # ~ else:
                    # ~ raise osv.except_osv(_('Warning!'),
                    # _('Invoice dates should be equal'))

        if not values.get('invoice_datetime', False) and\
                not values.get('date_invoice', False):
            res['date_invoice'] = fields.Date.context_today(self)
            res['invoice_datetime'] = fields.Datetime.now()

        return res

    @api.multi
    def action_move_create(self):
        for inv in self:
            if inv.type in ('out_invoice', 'out_refund'):
                vals_date = self.assigned_datetime(
                    {'invoice_datetime': inv.invoice_datetime,
                     'date_invoice': inv.date_invoice})
                self.write(vals_date)
        return super(AccountInvoice, self).action_move_create()
