# -*- coding: utf-8 -*-
# Copyright 2016 Vauxoo (Moises Lopez <moylop260@vauxoo.com>
#                        Osval Reyes <osval@vauxoo.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
import time
from openerp import _, api, fields, models, tools
from openerp.exceptions import Warning as UserError
from pytz import timezone
import pytz


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    def compute(self, value, date_ref=False):
        if date_ref:
            try:
                date_ref = time.strftime('%Y-%m-%d', time.strptime(
                    date_ref, '%Y-%m-%d %H:%M:%S'))
            except BaseException:
                pass
        return super(AccountPaymentTerm, self).compute(value, date_ref)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _compute_get_field_params(self):
        account_setting_obj = self.env["account.config.settings"]
        key_by_company_id = "acc_invoice.date_invoice_type_" + \
            str(account_setting_obj._default_company())
        res = {}
        for invoice_id in self.ids:
            res[invoice_id] = self.env["ir.config_parameter"].get_param(
                key_by_company_id, default='date')
        return res

    invoice_datetime = fields.Datetime(
        'Date time of invoice',
        states={'open': [('readonly', True)],
                'close': [('readonly', True)]},
        help="Keep empty to use the current date")

    date_invoice_tz = fields.Datetime(
        string='Date Invoiced with TZ',
        help='Date of Invoice with Time Zone')

    date_type = fields.Char(compute="_compute_get_field_params",
                            default=lambda self: self._get_default_type(),
                            help="Indicates if date or datetime is being used")

    @api.model
    def _get_datetime_with_user_tz(self, datetime_invoice):
        if not datetime_invoice:
            return False
        time_tz = self.env.user.tz_offset
        hours_tz = int(time_tz[:-2])
        minut_tz = int(time_tz[-2:])
        if time_tz[0] == '-':
            minut_tz = minut_tz * -1
        return (datetime_invoice + timedelta(hours=hours_tz, minutes=minut_tz)
                ).strftime('%Y-%m-%d %H:%M:%S')

    @api.model
    def create(self, vals):
        if 'invoice_datetime' in vals.keys():
            datetime_inv = vals.get("invoice_datetime") and \
                datetime.strptime(vals.get("invoice_datetime"),
                                  "%Y-%m-%d %H:%M:%S") or False
            vals.update({
                'date_invoice_tz': self._get_datetime_with_user_tz(
                    datetime_inv)
            })
        return super(AccountInvoice, self).create(vals)

    @api.multi
    def write(self, vals):
        for invoice_id in self:
            datetime_inv = invoice_id.invoice_datetime and \
                datetime.strptime(invoice_id.invoice_datetime,
                                  "%Y-%m-%d %H:%M:%S") or False
            if datetime_inv and not invoice_id.date_invoice_tz:
                vals.update({
                    'date_invoice_tz': self._get_datetime_with_user_tz(
                        datetime_inv)
                })
        return super(AccountInvoice, self).write(vals)

    @api.model
    def _get_default_type(self):
        account_setting_obj = self.env["account.config.settings"]
        key_by_company_id = "acc_invoice.date_invoice_type_" + \
            str(account_setting_obj._default_company())
        return self.env["ir.config_parameter"].get_param(
            key_by_company_id, default='date')

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default.update({
            'invoice_datetime': False,
            'date_invoice': False,
            'date_invoice_tz': False
        })
        return super(AccountInvoice, self).copy(default)

    @api.model
    def _get_time_zone(self):
        userstz = self.env.user.partner_id.tz
        if not userstz:
            return False
        result = 0
        hours = timezone(userstz)
        fmt = '%Y-%m-%d %H:%M:%S %Z%z'
        now = datetime.now()
        loc_dt = hours.localize(datetime(now.year, now.month,
                                         now.day, now.hour,
                                         now.minute, now.second))
        timezone_loc = (loc_dt.strftime(fmt))
        diff_timezone_original = timezone_loc[-5:-2]
        timezone_original = int(diff_timezone_original)
        str_datetime = str(datetime.now(pytz.timezone(userstz)))
        str_datetime = str_datetime[-6:-3]
        timezone_present = int(str_datetime) * -1
        result = timezone_original + ((
            timezone_present + timezone_original) * -1)
        return result

    def assigned_datetime(self, values):
        res = {}
        if values.get('date_invoice', False) and\
                not values.get('invoice_datetime', False):
            user_hour = self._get_time_zone()
            time_invoice = datetime.utcnow().time()

            date_invoice = datetime.strptime(
                values['date_invoice'], '%Y-%m-%d').date()

            dt_invoice = datetime.combine(
                date_invoice, time_invoice).strftime('%Y-%m-%d %H:%M:%S')

            res['invoice_datetime'] = dt_invoice
            res['date_invoice'] = values['date_invoice']

        if values.get('invoice_datetime', False) and not\
                values.get('date_invoice', False):
            date_invoice = fields.datetime.context_timestamp(
                datetime.strptime(
                    values['invoice_datetime'],
                    tools.DEFAULT_SERVER_DATETIME_FORMAT))
            res['date_invoice'] = date_invoice
            res['invoice_datetime'] = values['invoice_datetime']

        if 'invoice_datetime' in values and 'date_invoice' in values and\
                values['invoice_datetime'] and values['date_invoice']:
            date_invoice = datetime.strptime(
                values['invoice_datetime'],
                '%Y-%m-%d %H:%M:%S').date().strftime('%Y-%m-%d')
            if date_invoice != values['date_invoice']:
                if self.date_type == 'datetime':
                    date_invoice = fields.datetime.context_timestamp(
                        datetime.strptime(
                            values['invoice_datetime'],
                            tools.DEFAULT_SERVER_DATETIME_FORMAT))
                    res['date_invoice'] = date_invoice
                    res['invoice_datetime'] = values['invoice_datetime']
                elif self[0].date_type == 'date':
                    user_hour = self._get_time_zone()
                    time_invoice = datetime.time(abs(user_hour), 0, 0)

                    date_invoice = datetime.strptime(
                        values['date_invoice'], '%Y-%m-%d').date()

                    dt_invoice = datetime.combine(
                        date_invoice,
                        time_invoice).strftime('%Y-%m-%d %H:%M:%S')

                    res['invoice_datetime'] = dt_invoice
                    res['date_invoice'] = values['date_invoice']
                else:
                    raise UserError(_('Warning!'),
                                    _('Invoice dates should be equal'))

        if not values.get('invoice_datetime', False) and\
                not values.get('date_invoice', False):
            res['date_invoice'] = fields.Date.context_today(self)
            res['invoice_datetime'] = fields.datetime.now()

        return res

    @api.multi
    def action_move_create(self):
        for invoice_id in self.filtered(
                lambda r: r.type in ('out_invoice', 'out_refund')):
            vals_date = self.assigned_datetime({
                'invoice_datetime': invoice_id.invoice_datetime,
                'date_invoice': invoice_id.date_invoice
            })
            invoice_id.write(vals_date)
        return super(AccountInvoice, self).action_move_create()
