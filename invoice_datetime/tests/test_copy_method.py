# coding: utf-8

from openerp.tests.common import TransactionCase


class TestInvoiceDatetimeCopy(TransactionCase):
    """Test for invoice_datetime copy method.
    """

    # Method pseudo-constructor of test setUp
    def setUp(self):
        # Define global variables to test methods
        super(TestInvoiceDatetimeCopy, self).setUp()
        self.invoice = self.env['account.invoice']

    def test_10_copy_method(self):
        """Test to verify that the copy method works fine
        """
        invoice = self.env.ref('account.invoice_2')
        invoice.copy()
