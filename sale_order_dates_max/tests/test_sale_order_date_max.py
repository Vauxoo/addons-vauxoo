# coding: utf-8

from openerp.tests.common import TransactionCase
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestCommitmentDateMax(TransactionCase):

    def setUp(self):
        super(TestCommitmentDateMax, self).setUp()
        self.sale_order = self.env['sale.order']
        self.sale_order_line = self.env['sale.order.line']
        self.product = self.env['product.product']
        self.partner_id = self.ref("base.res_partner_2")

        self.product_1 = self.product.create({
            'name': 'product 1'})
        self.product_2 = self.product.create({
            'name': 'product 2'})

    def test_commitment_date(self):
        so_id = self.sale_order.create(
            {'partner_id': self.partner_id})
        self.sale_order_line.create({
            'order_id': so_id.id,
            'product_id': self.product_1.id,
            'product_uom_qty': 1,
            'delay': 1})
        self.sale_order_line.create({
            'order_id': so_id.id,
            'product_id': self.product_2.id,
            'product_uom_qty': 1,
            'delay': 2})

        order_datetime = datetime.strptime(
            so_id.date_order, DEFAULT_SERVER_DATETIME_FORMAT)
        date_order = order_datetime + timedelta(days=2)
        so_date = date_order.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.assertEquals(so_date, so_id.commitment_date)
