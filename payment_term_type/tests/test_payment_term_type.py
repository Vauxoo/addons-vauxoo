# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp.tests.common import TransactionCase


class TestPaymentTermType(TransactionCase):
    """This Tests validate the payment type dependig
        payment terms line to compute
    """

    def setUp(self):
        super(TestPaymentTermType, self).setUp()

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
