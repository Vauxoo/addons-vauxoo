# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Jose Suniaga <josemiguel@vauxoo.com>
#
############################################################################

from dateutil.relativedelta import relativedelta
from openerp import api, fields, models


class ResourceCalendar(models.Model):
    """ Calendar model for a resource. It has:

    - attendance_ids: list of resource.calendar.attendance that are a working
    interval in a given weekday.
    - leave_ids: list of leaves linked to this calendar. A leave can be general
    or linked to a specific resource, depending on its resource_id.

    All methods in this class use intervals. An interval is a tuple holding
    (begin_datetime, end_datetime). A list of intervals is therefore a list of
    tuples, holding several intervals of work or leaves.

    Extracted from addons/resource/resource.py at 8.0
    """

    _inherit = "resource.calendar"

    @api.multi
    def get_holidays(self, year, add_offset=False):
        self.ensure_one()
        leave_obj = self.env['resource.calendar.leaves']
        holidays = []
        tz_offset = 0
        if add_offset:
            tz_offset = fields.Datetime.context_timestamp(
                self, fields.Datetime.from_string(fields.Datetime.now())).\
                utcoffset().total_seconds()
        start_dt = fields.Datetime.from_string(fields.Datetime.now()).\
            replace(year=year, month=1, day=1, hour=0, minute=0, second=0) + \
            relativedelta(seconds=tz_offset)
        end_dt = start_dt + relativedelta(years=1) - relativedelta(seconds=1)
        leaves_domain = [
            ('calendar_id', '=', self.id),
            ('resource_id', '=', False),
            ('date_from', '>=', fields.Datetime.to_string(start_dt)),
            ('date_to', '<=', fields.Datetime.to_string(end_dt))]
        for leave in leave_obj.search(leaves_domain):
            date_from = fields.Datetime.from_string(leave.date_from)
            holidays.append((date_from.date(), leave.name))
        return holidays

    @api.multi
    def get_previous_day(self, day_date):
        """ Get previous date of day_date, based on resource.calendar. If no
        calendar is provided, just return the previous day.

        Inherited from addons/resource/resource.py at 8.0

        :param date day_date: current day as a date
        :return date: previous day of calendar, or just previous day """

        res = super(ResourceCalendar, self).get_previous_day(day_date)
        # TODO: figure out why this function return list instead date
        previous_day = isinstance(res, list) and res[0] or res
        for calendar in self:
            previous_day = calendar.is_holiday(previous_day) and \
                calendar.get_next_day(previous_day) or previous_day
        return previous_day

    @api.multi
    def get_next_day(self, day_date):
        """ Get following date of day_date, based on resource.calendar. If no
        calendar is provided, just return the next day.

        Inherited from addons/resource/resource.py at 8.0

        :param date day_date: current day as a date
        :return date: next day of calendar, or just next day
        """

        res = super(ResourceCalendar, self).get_next_day(day_date)
        # TODO: figure out why this function return list instead date
        next_day = isinstance(res, list) and res[0] or res
        for calendar in self:
            next_day = calendar.is_holiday(next_day) and \
                calendar.get_next_day(next_day) or next_day
        return next_day

    @api.multi
    def is_holiday(self, day_date):
        holidays = self.get_holidays(day_date.year)
        return any([holiday[0] == day_date for holiday in holidays])

    @api.multi
    def compute_working_days(self, days, start_dt):
        self.ensure_one()
        day_date = start_dt.date()
        end_dt = start_dt
        compute_day = days > 0 and self.get_next_day or self.get_previous_day
        days = abs(days)
        while days > 0:
            # get working day
            day_date = compute_day(day_date)
            end_dt = start_dt.replace(
                year=day_date.year, month=day_date.month, day=day_date.day)
            days -= 1
        return end_dt
