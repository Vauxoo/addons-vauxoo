# -*- coding: utf-8 -*-
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
        self.payment_term = self.env['account.payment.term']
        self.payment_term_line = self.env['account.payment.term.line']

    def test_payment_term_type_cash(self):
        """
            This test validate payment type in cash
        """

        payment_term_id = self.payment_term.create({
            'name': 'Payment Term Cash',
            })
        self.payment_term_line.create({
            'value': 'balance',
            'payment_id': payment_term_id.id})
        self.assertEqual(
            payment_term_id.payment_type, 'cash',
            'Payment term should be in cash')

    def test_payment_term_type_credit(self):
        """
            This test validate payment type in credit
        """

        payment_term_id = self.payment_term.create({
            'name': 'Payment Term credit',
            })
        self.payment_term_line.create({
            'value': 'procent',
            'payment_id': payment_term_id.id})
        self.payment_term_line.create({
            'value': 'balance',
            'payment_id': payment_term_id.id})
        self.assertEqual(
            payment_term_id.payment_type, 'credit',
            'Payment term should be in credit')
