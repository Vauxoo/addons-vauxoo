# -*- coding: utf-8 -*-
# © 2015 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)


from openerp.tests import common
from openerp import exceptions


class TestSaleCashRegister(common.TransactionCase):
    def setUp(self):
        super(TestSaleCashRegister, self).setUp()

        self.sale_register_session = self.env['sale.register.session']
        self.sale_order = self.env['sale.order']
        self.product = self.env['product.product']
        self.sale_order_line = self.env['sale.order.line']
        self.partner_id = self.ref("base.res_partner_2")
        self.product_1 = self.product.create({
            'name': 'product 1',
            'type': 'product'})
        self.session_id = self.sale_register_session.create({
            'user_id': self.uid
        })
        self.session_2_id = self.sale_register_session.create({
            'user_id': self.uid
        })

    def test_sale_register_session(self):
        'This test validate only one session opened per user'

        self.session_id.action_open()
        msg = 'You cannot create two active sessions '
        with self.assertRaisesRegexp(exceptions.ValidationError, msg):
            self.session_2_id.action_open()

    def test_sale_register_session_sale_order(self):
        'This test validate that session opened is set in '\
            'Sale Order created and Picking'

        self.session_2_id.action_open()

        so_id = self.sale_order.create(
            {'partner_id': self.partner_id,
             'order_policy': 'manual'})
        self.sale_order_line.create({
            'order_id': so_id.id,
            'product_id': self.product_1.id,
            'product_uom_qty': 1,
            'delay': 1})
        self.assertEquals(so_id.session_id, self.session_2_id)

        so_id.action_button_confirm()

        self.assertEquals(len(self.session_2_id.sale_ids), 1)
