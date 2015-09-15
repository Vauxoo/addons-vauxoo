# -*- encoding: utf-8 -*-
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


class TestPaymentTermType(TransactionCase):
    """
        This Tests validate the payment type dependig
        payment terms line to compute
    """
    def setUp(self):
        super(TestPaymentTermType, self).setUp()
        self.account_invoice = self.env['account.invoice']
        self.account_invoice_line = self.env['account.invoice.line']
        self.payment_term_cash = self.env.ref(
            'payment_term_type.payment_term_cash')
        self.payment_term_credit = self.env.ref(
            'payment_term_type.payment_term_credit')

        self.partner_agrolait = self.env.ref("base.res_partner_2")
        self.journal_id = self.env.ref("account.bank_journal")
        self.account_id = self.env.ref("account.a_recv")
        self.product_id = self.env.ref("product.product_product_6")

    def test_payment_term_type_cash(self):
        """
            This test validate payment type in cash
        """
        # invoice state 'Draft'
        invoice_id = self.account_invoice.create(
            {'partner_id': self.partner_agrolait.id,
             'account_id': self.account_id.id,
             'payment_term': self.payment_term_cash.id,
             'journal_id': self.journal_id.id, })
        self.account_invoice_line.create(
            {'product_id': self.product_id.id,
             'quantity': 1,
             'price_unit': 100,
             'invoice_id': invoice_id.id,
             'name': 'product that cost 100', })
        # payment term Cash and invoice state Draft  ==> False
        self.assertFalse(
            invoice_id.allow_print_ok)

        # payment term Cash and invoice state Cancel ==> False
        invoice_id.signal_workflow('invoice_cancel')
        self.assertFalse(
            invoice_id.allow_print_ok)
        # Reset invoice to Draft
        invoice_id.action_cancel_draft()
        self.assertEquals(
            invoice_id.state, 'draft')

        # payment term Cash and invoice state Open ==> False
        invoice_id.signal_workflow('invoice_open')
        self.assertFalse(
            invoice_id.allow_print_ok)

        # payment term Cash and invoice state Paid ==> True
        invoice_id.confirm_paid()
        self.assertTrue(invoice_id.allow_print_ok)

    def test_payment_term_type_credit(self):
        """
            This test validate payment type in cash
        """
        # invoice state 'Draft'
        invoice_id = self.account_invoice.create(
            {'partner_id': self.partner_agrolait.id,
             'account_id': self.account_id.id,
             'payment_term': self.payment_term_credit.id,
             'journal_id': self.journal_id.id, })
        self.account_invoice_line.create(
            {'product_id': self.product_id.id,
             'quantity': 1,
             'price_unit': 100,
             'invoice_id': invoice_id.id,
             'name': 'product that cost 100', })
        # payment term Cash and invoice state Draft  ==> False
        self.assertFalse(
            invoice_id.allow_print_ok)

        # payment term Cash and invoice state Cancel ==> False
        invoice_id.signal_workflow('invoice_cancel')
        self.assertFalse(
            invoice_id.allow_print_ok)
        # Reset invoice to Draft
        invoice_id.action_cancel_draft()
        self.assertEquals(
            invoice_id.state, 'draft')

        # payment term Cash and invoice state Open ==> True
        invoice_id.signal_workflow('invoice_open')
        self.assertTrue(
            invoice_id.allow_print_ok)

        # payment term Cash and invoice state Paid ==> True
        self.assertTrue(invoice_id.allow_print_ok)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
