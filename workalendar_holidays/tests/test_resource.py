# -*- coding: utf-8 -*-
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
from openerp import fields
from openerp.addons.resource.tests import common


class TestResource(common.TestResourceCommon):

    def setUp(self):
        super(TestResource, self).setUp()

        self.resource_calendar = self.env['resource.calendar']
        self.resource_leaves = self.env['resource.calendar.leaves']

        # Some date for demo
        self.date3 = fields.Datetime.from_string('2016-10-04 10:11:12')
        self.date4 = fields.Datetime.from_string('2016-10-07 10:11:12')

        # Set as holiday a week after date3
        self.holiday_start = fields.Datetime.from_string('2016-10-11 00:00:00')
        self.holiday_end = fields.Datetime.from_string('2016-10-11 23:59:59')

        self.leave4 = self.resource_leaves.create({
            'name': 'Pre-Columbus Day 2016',
            'date_from': self.holiday_start,
            'date_to': self.holiday_end,
            'calendar_id': self.calendar_id})

    def test_00_next_day(self):
        """ Testing next day computation """

        calendar = self.resource_calendar.browse(self.calendar_id)

        # next day after date3 is date4
        date = calendar.get_next_day(day_date=self.date3.date())
        self.assertEqual(date, self.date4.date(),
                         'resource_calendar: wrong next day computing')

        # next day after date4 is date4 + 7
        date = calendar.get_next_day(day_date=self.date4.date())
        self.assertEqual(date, self.date4.date() + relativedelta(days=7),
                         'resource_calendar: wrong next day computing')

        # next day after date3 - 1 is date3
        date = calendar.get_next_day(
            day_date=self.date3.date() + relativedelta(days=-1))
        self.assertEqual(date, self.date3.date(),
                         'resource_calendar: wrong next day computing')

    def test_10_previous_day(self):
        """ Testing previous day computation """

        calendar = self.resource_calendar.browse(self.calendar_id)

        # previous day before date3 is date4 - 7
        date = calendar.get_previous_day(day_date=self.date3.date())
        self.assertEqual(date, self.date4.date() + relativedelta(days=-7),
                         'resource_calendar: wrong previous day computing')

        # previous day before date4 is date3
        date = calendar.get_previous_day(day_date=self.date4.date())
        self.assertEqual(date, self.date3.date(),
                         'resource_calendar: wrong previous day computing')

        # previous day before date4 + 7 is date 4
        date = calendar.get_previous_day(
            day_date=self.date4.date() + relativedelta(days=7))
        self.assertEqual(date, self.date4.date(),
                         'resource_calendar: wrong previous day computing')

        # previous day before date3 + 1 is day3
        date = calendar.get_previous_day(
            day_date=self.date3.date() + relativedelta(days=1))
        self.assertEqual(date, self.date3.date(),
                         'resource_calendar: wrong previous day computing')

    def test_20_working_days(self):
        """ Testing previous day computation """

        calendar = self.resource_calendar.browse(self.calendar_id)

        # 1 working day after date3 is date4
        datetime = calendar.compute_working_days(1, self.date3)
        self.assertEqual(datetime, self.date4,
                         'resource_calendar: wrong working days computing')

        # 2 working days after date3 is date4 + 7
        datetime = calendar.compute_working_days(2, self.date3)
        self.assertEqual(datetime, self.date4 + relativedelta(days=7),
                         'resource_calendar: wrong working days computing')

        # 2 working days before date3 is date3 - 7
        datetime = calendar.compute_working_days(-2, self.date3)
        self.assertEqual(datetime, self.date3 + relativedelta(days=-7),
                         'resource_calendar: wrong working days computing')

        # 2 working days before date4 is date4 - 7
        datetime = calendar.compute_working_days(-2, self.date4)
        self.assertEqual(datetime, self.date4 + relativedelta(days=-7),
                         'resource_calendar: wrong working days computing')

        # 2 working days before date4 + 7 is date3
        datetime = calendar.compute_working_days(
            -2, self.date4 + relativedelta(days=7))
        self.assertEqual(datetime, self.date3,
                         'resource_calendar: wrong working days computing')

    def test_30_holidays(self):
        """ Testing company holidays """

        calendar = self.resource_calendar.browse(self.calendar_id)
        holidays = calendar.get_holidays(2016)

        # date3 is a working day
        self.assertFalse(calendar.is_holiday(self.date3.date()))

        # date3 + 1 is not a working day, neither holiday
        self.assertFalse(calendar.is_holiday(
            self.date3.date() + relativedelta(days=1)))

        # date3 + 7 is not a working day, because is a holiday
        self.assertTrue(calendar.is_holiday(
            self.date3.date() + relativedelta(days=7)))

        self.assertEqual(len(holidays), 1)
