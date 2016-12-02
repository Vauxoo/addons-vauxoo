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
from openerp.addons.resource.tests import common


class TestHolidayImport(common.TestResourceCommon):

    def setUp(self):
        super(TestHolidayImport, self).setUp()

        self.resource_calendar = self.env['resource.calendar']
        self.holiday_wizard = self.env['wizard.workalendar.holiday.import']

    def test_00_holiday_import(self):
        """ Testing public holidays importation """

        calendar = self.resource_calendar.browse(self.calendar_id)
        country_group_id = self.env.ref('workalendar_holidays.america').id
        year = 2016

        # check that there are no holidays loaded in the calendar
        self.assertFalse(calendar.get_holidays(year))

        # create wizard to load holidays in the calendar
        wiz = self.holiday_wizard.create({
            'start_date': '%d-01-01' % (year),
            'interval_number': 1,
            'interval_type': 'years',
            'calendar_id': self.calendar_id,
            'country_group_id': country_group_id,
            'country_id': self.env.ref('base.mx').id,
        })

        # load holidays in calendar
        wiz.holiday_import()

        # check that now, the holidays have been loaded in the calendar
        self.assertTrue(calendar.get_holidays(year))
