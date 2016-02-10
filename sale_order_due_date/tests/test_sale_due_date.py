# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2016 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Luis Torres <luis_t@vauxoo.com>
############################################################################
from openerp.tests import common
from datetime import date, timedelta, datetime


class TestSaleDueDate(common.TransactionCase):

    def setUp(self):
        super(TestSaleDueDate, self).setUp()
        self.conf = self.env.ref('sale_order_due_date.days_due_date')
        self.sale = self.env.ref('sale.sale_order_4')

    def test_update_days(self):
        'Test update the value in ir.config_parameter, to 5 days'
        self.env['sale.config.settings'].create({
            'days_due_date_sale': 5}).execute()
        self.assertEquals(5, int(self.conf.value), 'The value was not updated')

    def test_check_due_date_by_default(self):
        'Test to check that date due is fill by default and is correct'
        self.test_update_days()
        sale = self.sale.copy()
        self.assertEquals(
            sale.due_date, datetime.strftime(
                date.today() + timedelta(days=int(self.conf.value)),
                '%Y-%m-%d'), 'Incorrect due date')
