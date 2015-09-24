# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (c) 2012-TODAY OpenERP S.A. <http://openerp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests.common import TransactionCase


class TestPaymentTermType(TransactionCase):
    """
        This Tests validate the payment type dependig
        payment terms line to compute
    """

    def setUp(self):
        super(TestPaymentTermType, self).setUp()

    def test_payment_term_type_cash(self):
        """
            This test validate payment type in cash
        """
        self.payment_term_cash = self.env.ref(
            'payment_term_type.payment_term_cash')
        self.assertEqual(
            self.payment_term_cash.payment_type, 'cash',
            'Payment term should be in cash')

    def test_payment_term_type_credit(self):
        """
            This test validate payment type in credit
        """
        self.payment_term_credit = self.env.ref(
            'payment_term_type.payment_term_credit')
        self.assertEqual(
            self.payment_term_credit.payment_type, 'credit',
            'Payment term should be in credit')
