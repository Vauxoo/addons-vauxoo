# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Jose Suniaga <josemiguel@vauxoo.com>
#    planned by: Jose Suniaga <josemiguel@vauxoo.com>
############################################################################

import logging

from dateutil.relativedelta import relativedelta
from openerp import _, api, fields, models
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)

try:
    from workalendar import africa
    from workalendar import asia
    from workalendar import america
    from workalendar import canada
    from workalendar import europe
    from workalendar import oceania
    from workalendar import usa
except ImportError:
    _logger.info('Cannot import workalendar')

_INTERVALS = {
    'days': lambda interval: relativedelta(days=interval),
    'weeks': lambda interval: relativedelta(days=7*interval),
    'months': lambda interval: relativedelta(months=interval),
    'years': lambda interval: relativedelta(months=12*interval),
}


class WorkalendarHolidayImport(models.TransientModel):

    _name = 'wizard.workalendar.holiday.import'

    @api.multi
    @api.depends('start_date', 'interval_number', 'interval_type')
    def _compute_end_date(self):
        for wiz in self:
            wiz.end_date = fields.Date.from_string(wiz.start_date) + \
                _INTERVALS[wiz.interval_type](wiz.interval_number)

    start_date = fields.Date(
        string='Start Date', default=fields.Date.today, readonly=1)
    end_date = fields.Date(
        string='End Date', compute='_compute_end_date')
    interval_number = fields.Integer('Interval', default=1)
    interval_type = fields.Selection([
        ('days', 'Day(s)'),
        ('weeks', 'Week(s)'),
        ('months', 'Month(s)'),
        ('years', 'Year(s)')],
        string='Type', default='days', required=True)
    calendar_id = fields.Many2one(
        'resource.calendar', string="Work Time")
    country_group_id = fields.Many2one(
        'res.country.group', string="Continent", required=True)
    country_id = fields.Many2one(
        'res.country', string="Country", required=True)

    @api.model
    def _get_workalendar_module(self, continent_name, country_id=False):
        country_libs = {
            self.env.ref('base.ca').id: canada,
            self.env.ref('base.us').id: usa
        }
        if country_id in country_libs:
            return country_libs[country_id]
        name = str(continent_name).lower()
        libs = (africa, america, asia, europe, oceania)
        module = [lib for lib in libs if (lib.__name__).split('.')[1] == name]
        return module and module[0] or False

    @api.model
    def _get_workalendar_instance(self, continent, country, state=False):
        instance = False
        module = self._get_workalendar_module(continent.name)
        if not module:
            raise ValidationError(
                _("Sorry, no support for %s continent") % continent.name)

        # TODO: at version 9.0 can be replace the following search with the
        # ir.translation function _get_terms_query
        trans = self.env['ir.translation'].search([
            ('type', '=', 'model'),
            ('name', '=', 'res.country,name'),
            ('res_id', '=', country.id)], limit=1)
        country_name = trans.src and \
            str(''.join(trans.src.title().split(' '))) or country.name
        try:
            class_ = getattr(module, country_name)
            instance = class_()
        except AttributeError:
            raise ValidationError(
                _("Sorry, no support for country: %s") % country.name)
        return instance

    @api.multi
    def holiday_import(self):
        for wiz in self:
            leaves = self.env['resource.calendar.leaves']
            work_time = wiz.calendar_id
            continent = wiz.country_group_id
            country = wiz.country_id
            calendar = self._get_workalendar_instance(continent, country)
            start_year = fields.Datetime.from_string(wiz.start_date).year
            end_year = fields.Datetime.from_string(wiz.end_date).year
            # get public holidays, avoid holidays out of range of wizard dates
            public_holidays = [
                holiday for year in range(start_year, end_year + 1)
                for holiday in calendar.holidays(year)
                if holiday[0] <= fields.Date.from_string(wiz.end_date) and
                holiday[0] >= fields.Date.from_string(wiz.start_date)]
            for holiday_date, holiday_name in public_holidays:
                utc_dt = fields.Datetime.from_string(
                    fields.Datetime.to_string(holiday_date))
                user_dt = fields.Datetime.context_timestamp(
                    self, utc_dt)
                datetime_from = utc_dt - \
                    relativedelta(seconds=user_dt.utcoffset().total_seconds())
                datetime_to = datetime_from + relativedelta(days=1) - \
                    relativedelta(seconds=1)
                date_from = fields.Datetime.to_string(datetime_from)
                date_to = fields.Datetime.to_string(datetime_to)
                if not leaves.search_count([
                        ('resource_id', '=', False),
                        ('calendar_id', '=', work_time.id),
                        ('date_from', '>=', date_from),
                        ('date_to', '<=', date_to)]):
                    leaves.create({
                        'resource_id': False,
                        'name': '%s %d' % (holiday_name, holiday_date.year),
                        'calendar_id': work_time.id,
                        'date_from': date_from,
                        'date_to': date_to})
        return True
