# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2016 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Luis Torres <luis_t@vauxoo.com>
############################################################################
from datetime import date, timedelta, datetime
from openerp.tests import common


class TestSaleDueDate(common.TransactionCase):

    def setUp(self):
        super(TestSaleDueDate, self).setUp()
        self.conf = self.env.ref('sale_order_due_date.days_due_date')
        self.sale_obj = self.env['sale.order']
        self.sale = self.sale_obj.create({
            'partner_id': self.ref('base.res_partner_15'),
            'partner_invoice_id': self.ref('base.res_partner_address_25'),
            'partner_shipping_id': self.ref('base.res_partner_address_25'),
            'user_id': self.ref('base.user_root'),
            'section_id': self.ref('sales_team.section_sales_department'),
            'pricelist_id': self.ref('product.list0'),
            'order_line': [(0, 0, {
                'product_id': self.ref('product.product_product_consultant'),
                'product_uom_qty': 16.0,
                'product_uos_qty': 16.0,
                'price_unit': 75.0,
                'product_uom': self.ref('product.product_uom_hour'),
            })],
        })

    def test_update_days(self):
        """Test update the value in ir.config_parameter, to 5 days"""
        self.env['sale.config.settings'].create({
            'days_due_date_sale': 5}).execute()
        self.assertEquals(5, int(self.conf.value), 'The value was not updated')

    def test_check_due_date_by_default(self):
        """Test to check that date due is fill by default and is correct"""
        self.test_update_days()
        sale = self.sale.copy()
        self.assertEquals(
            sale.due_date, datetime.strftime(
                date.today() + timedelta(days=int(self.conf.value)),
                '%Y-%m-%d'), 'Incorrect due date')
