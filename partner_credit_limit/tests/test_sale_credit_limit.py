# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: hugo@vauxoo.com
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################

from openerp.tests.common import TransactionCase
from datetime import datetime, timedelta


class TestSalesCreditLimits(TransactionCase):
    """This test Validate credit limit, late pyaments and credit
        overloaded.
    """
    def setUp(self):
        super(TestSalesCreditLimits, self).setUp()
        self.account_invoice = self.env['account.invoice']
        self.sale_order = self.env['sale.order']
        self.sale_order_line = self.env['sale.order.line']
        self.account_invoice_line = self.env['account.invoice.line']
        self.payment_term_credit = self.env.ref(
            'account.account_payment_term_advance')

        self.partner_china = self.env.ref("base.res_partner_3")
        self.journal_id = self.env.ref("account.bank_journal")
        self.account_id = self.env.ref("account.a_recv")
        self.product_id = self.env.ref("product.product_product_6")

    def test_credit_limit_overloaded(self):
        """This test validate the partner has credit overloaded
            and can not confirm the sale order

        """
        # CASE WHERE PARTNER HAVE CREDIT OVERLOADED
        # set credit limit in 500
        self.partner_china.credit_limit = 200.00

        # sale order with amount total of 600.00
        sale_id = self.sale_order.create(
            {'partner_id': self.partner_china.id,
             'order_policy': 'manual',
             'payment_term': self.payment_term_credit.id})
        self.sale_order_line.create(
            {'product_id': self.product_id.id,
             'product_uos_qty': 1,
             'price_unit': 600,
             'order_id': sale_id.id,
             'name': 'product that cost 100', })
        # should not confirm sale order
        # credit limit exceded
        # credit_limit = 500
        # amount_total = 600
        sale_id.action_button_confirm()
        mail_message = self.env['mail.message'].search([
            ('model', '=', 'sale.order'),
            ('res_id', '=', sale_id.id),
            ('subject', '=', 'Exception Credit'),
            ('type', '=', 'notification'),
        ])
        self.assertIn(
            'The Sale order pass to state of Exception Credit.',
            mail_message.body)

    def test_partner_with_late_payments(self):
        """This test validate that the partner has not late payments

        """
        # CASE WHERE PARTNER DOES NOT HAVE LATE PAYMENTS AND CREDIT OVERLOADED
        # set credit limit in 500
        self.partner_china.credit_limit = 700.00

        # invoice with amount total of 400.00 and date decreased one day
        # to get a late payment
        invoice_id = self.account_invoice.create(
            {'partner_id': self.partner_china.id,
             'account_id': self.account_id.id,
             'date_invoice': (datetime.now() - timedelta(days=2)).
                strftime("%Y-%m-%d"),
             'payment_term': self.payment_term_credit.id,
             'journal_id': self.journal_id.id, })
        self.account_invoice_line.create(
            {'product_id': self.product_id.id,
             'quantity': 4,
             'price_unit': 100,
             'invoice_id': invoice_id.id,
             'name': 'product that cost 100', })
        # Validate the invoice.
        invoice_id.signal_workflow('invoice_open')

        # At this moment there are late paymets since the invoice
        # was validate one day before

        # CASE WHERE PARTNER HAVE LATE PAYMENTS
        # sale order with amount total of 600.00
        sale_id = self.sale_order.create(
            {'partner_id': self.partner_china.id,
             'order_policy': 'manual',
             'payment_term': self.payment_term_credit.id})
        self.sale_order_line.create(
            {'product_id': self.product_id.id,
             'product_uos_qty': 1,
             'price_unit': 200,
             'order_id': sale_id.id,
             'name': 'product that cost 100', })
        # should not confirm sale order should fail,
        # couse there are late payments
        # since the invoice 1 was validate with curent day minus 2 days
        sale_id.action_button_confirm()
        mail_message = self.env['mail.message'].search([
            ('model', '=', 'sale.order'),
            ('res_id', '=', sale_id.id),
            ('subject', '=', 'Exception Credit'),
            ('type', '=', 'notification')
        ])
        self.assertIn('The Sale order pass to state of Exception Credit.',
                      mail_message.body)
