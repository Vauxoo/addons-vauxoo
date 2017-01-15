# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from odoo import exceptions
from . import common


class TestCreditLimits(common.TestCommon):
    """This test Validate credit limit, late pyaments and credit
        overloaded.
    """
    def setUp(self):
        super(TestCreditLimits, self).setUp()
        self._load('account', 'test', 'account_minimal_test.xml')
        self.payment_term_credit = self.env.ref(
            'account.account_payment_term_advance')

        self.partner_china = self.env.ref("base.res_partner_3")
        self.journal_id = self.env.ref("account.bank_journal")
        self.account_id = self.env.ref("account.a_recv")
        self.account_sale_id = self.env.ref("account.a_sale")
        self.product_id = self.env.ref("product.product_product_6")

    def test_credit_limit_overloaded(self):
        """This test validate the partner has credit overloaded
            and can not validate the invoice

        """
        # CASE WHERE PARTNER HAVE CREDIT OVERLOADED
        # set credit limit in 500
        self.partner_china.credit_limit = 500.00

        # invoice with amount total of 600.00
        invoice_id = self.account_invoice.create(
            {'partner_id': self.partner_china.id,
             'account_id': self.account_id.id,
             'payment_term_id': self.payment_term_credit.id,
             'journal_id': self.journal_id.id, })
        self.account_invoice_line.create(
            {'product_id': self.product_id.id,
             'account_id': self.account_sale_id.id,
             'quantity': 6,
             'price_unit': 100,
             'invoice_id': invoice_id.id,
             'name': 'product that cost 100', })

        # should not validate the invoice
        # credit limit exceded
        # credit_limit = 500
        # amount_total = 600
        with self.assertRaises(exceptions.Warning):
            invoice_id.signal_workflow('invoice_open')

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
             'date_invoice': (
                 datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
             'payment_term_id': self.payment_term_credit.id,
             'journal_id': self.journal_id.id, })
        self.account_invoice_line.create(
            {'product_id': self.product_id.id,
             'account_id': self.account_sale_id.id,
             'quantity': 4,
             'price_unit': 100,
             'invoice_id': invoice_id.id,
             'name': 'product that cost 100', })
        # Validate the invoice.
        invoice_id.signal_workflow('invoice_open')

        # At this moment there are late paymets since the invoice
        # was validate one day before

        # CASE WHERE PARTNER HAVE LATE PAYMENTS
        # Crate second invoice
        invoice_id2 = self.account_invoice.create(
            {'partner_id': self.partner_china.id,
             'account_id': self.account_id.id,
             'payment_term_id': self.payment_term_credit.id,
             'journal_id': self.journal_id.id, })
        self.account_invoice_line.create(
            {'product_id': self.product_id.id,
             'account_id': self.account_sale_id.id,
             'quantity': 2,
             'price_unit': 100,
             'invoice_id': invoice_id2.id,
             'name': 'product that cost 100', })
        # Validate the invoice, should fail, couse there are late payments
        # since the invoice 1 was validate with curent day minus 2 days
        with self.assertRaises(exceptions.Warning):
            invoice_id2.signal_workflow('invoice_open')
