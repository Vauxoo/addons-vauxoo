# Copyright 2022 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.tests import Form


class PointOfSale(TransactionCase):

    def setUp(self):
        super().setUp()
        self.pos_order_obj = self.env['pos.order']
        self.pmp_obj = self.env['pos.make.payment']
        self.partner = self.env.ref('base.res_partner_12')
        self.session = Form(self.env.ref('point_of_sale.pos_config_main'))
        self.session.module_pos_discount = True
        self.session = self.session.save()
        self.discount_product_id = self.session.discount_product_id
        self.pos_categ_id = self.session.iface_start_categ_id
        self.pos_products = self.env['product.product'].search([
            ('available_in_pos', '=', True),
            ('pos_categ_id', '=', self.pos_categ_id.id),
        ])

    def create_session(self):
        session = self.session
        session = self.env['pos.session'].with_env(
            self.env(user=self.uid)).create({
                'user_id': self.uid,
                'config_id': session.id,
            })
        return session

    def create_order(self, discount, auto_paid=False):
        discount = discount or 0.10
        now = fields.Datetime.now()
        lines = []
        total_amount = 0
        # Adding some products to the order
        for product in self.pos_products:
            lines.append((0, 0, {
                'product_id': product.id,
                'price_unit': product.lst_price,
                'qty': 1.0,
                'price_subtotal': product.lst_price,
                'price_subtotal_incl': product.lst_price,
            }))
            total_amount += product.lst_price
        # Adding the discount of 10%, simulate the behavior of the global discount
        discount = -(total_amount * discount)
        lines.append((0, 0, {
            'product_id': self.discount_product_id.id,
            'price_unit': discount,
            'qty': 1.0,
            'price_subtotal': discount,
            'price_subtotal_incl': discount,
        }))
        data = {
            'partner_id': self.partner.id,
            'session_id': self.session.id,
            'date_order': now,
            'pos_reference': 'Order %s - %s' % (self.session.id, len(self.session.order_ids)),
            'to_invoice': True,
            'amount_total': total_amount,
            'amount_tax': 0.0,
            'amount_paid': 0.0,
            'amount_return': 0.0,
            'lines': lines
        }
        order = self.pos_order_obj.with_env(self.env(user=self.uid)).create(data)
        order._onchange_amount_all()
        if auto_paid:
            self.pay_order(order)
        return order

    def pay_order(self, order):
        payment = self.pmp_obj.with_env(self.env(user=self.uid)).with_context(
            active_id=order.id).create({
                'payment_method_id': order.session_id.config_id.payment_method_ids[0].id,
                'amount': order.amount_total
            })
        payment.check()
        order.action_pos_order_invoice()

    def test_001_order_global_discount(self):
        """Pos order, test global discount, prorate discount"""
        self.session = self.create_session()
        discount = 0.10
        order = self.create_order(discount, auto_paid=True)
        self.session.action_pos_session_close()
        invoice_discount_line = order.account_move.invoice_line_ids.filtered(
            lambda l: l.product_id == self.discount_product_id)
        # Now check the result account move
        self.assertEqual(order.account_move.state, 'posted')
        self.assertTrue(invoice_discount_line, 'Discount not applied')
        self.assertEqual(invoice_discount_line.price_total, 0, 'The discount line should be 0 in the invoice')
        total_sale = round(order.amount_total, 2)
        total_inv = round(sum(order.account_move.invoice_line_ids.mapped('price_total')), 2)
        self.assertEqual(total_sale, total_inv, 'The invoice total is different to the sale order.')
