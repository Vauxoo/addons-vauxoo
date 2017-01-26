# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class TestPaymentTermType(TransactionCase):
    """This Tests validate the payment type dependig
        payment terms line to compute
    """

    def setUp(self):
        super(TestPaymentTermType, self).setUp()
        self.company = self.env.ref('base.main_company')
        self.config_obj = self.env['account.config.settings']
        self.pay_term_obj = self.env['account.payment.term']

    def test_payment_term_type_cash(self):
        """This test validate payment type in cash
        """
        self.payment_term_cash = self.env.ref(
            'payment_term_type.payment_term_cash')
        self.assertEqual(
            self.payment_term_cash.payment_type, 'cash',
            'Payment term should be in cash')

    def test_payment_term_type_credit(self):
        """This test validate payment type in credit
        """
        self.payment_term_credit = self.env.ref(
            'payment_term_type.payment_term_credit')
        self.assertEqual(
            self.payment_term_credit.payment_type, 'credit',
            'Payment term should be in credit')

    def test_01_payment_term_type_bqp_cash(self):
        """This test validates that payment type is equal to cash if payment
        terms is based on quantity of payments and exists only one record.
        """
        self.config_obj.create({
            'company_id': self.company.id,
            'payment_type': 'bqp',
        })
        pay_term_id = self.pay_term_obj.create({
            'company_id': self.company.id,
            'name': 'Test payment term',
        })
        self.assertEqual(
            pay_term_id.payment_type,
            'cash',
            'The expected payment type should be cash.'
        )

    def test_02_payment_term_type_bqp_credit(self):
        """This test validates that payment type is equal to credit if payment
        terms is based on quantity of payments and exists two or more records.
        """
        self.config_obj.create({
            'company_id': self.company.id,
            'payment_type': 'bqp',
        })
        pay_term_id = self.pay_term_obj.create({
            'company_id': self.company.id,
            'name': 'Test payment term',
        })
        pay_term_id.write({
            "line_ids": [
                (0, 0, {
                    'value': 'percent',
                    'value_amount': 0.0,
                    'days': 0,
                    'sequence': 1,
                })
            ]
        })
        self.assertEqual(
            pay_term_id.payment_type,
            'credit',
            'The expected payment type should be credit.'
        )

    def test_03_payment_term_type_bdp_cash(self):
        """This test validates that payment type is equal to cash if payment
        terms is based on date of payments and days equal to 0
        """
        self.config_obj.create({
            'company_id': self.company.id,
            'payment_type': 'bdp',
        })
        pay_term_id = self.pay_term_obj.create({
            'company_id': self.company.id,
            'name': 'Test payment term',
        })
        self.assertEqual(
            pay_term_id.payment_type,
            'cash',
            'The expected payment type should be cash.'
        )

    def test_04_payment_term_type_bdp_credit(self):
        """This test validates that payment type is equal to credit if payment
        terms is based on date of payments and days is greater than 0
        """
        self.config_obj.create({
            'company_id': self.company.id,
            'payment_type': 'bdp',
        })
        pay_term_id = self.pay_term_obj.create({
            'company_id': self.company.id,
            'name': 'Test payment term',
        })
        pay_term_id.write({
            "line_ids": [
                (0, 0, {
                    'value': 'percent',
                    'value_amount': 0.0,
                    'days': 15,
                    'sequence': 1,
                })
            ]
        })
        self.assertEqual(
            pay_term_id.payment_type,
            'credit',
            'The expected payment type should be credit.'
        )
